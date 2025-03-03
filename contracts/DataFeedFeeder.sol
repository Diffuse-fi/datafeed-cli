// Copyright 2024 Diffuse.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// SPDX-License-Identifier: Apache-2.0

// taiko does not support MCOPY opcode
pragma solidity 0.8.20;

import {IAutomataDcapAttestationFee} from "./IAutomataDcapAttestationFee.sol";
import "./DataFeedStorage.sol";
import "../lib/sgx_verifier_deployer/lib/automata-dcap-attestation/contracts/types/Constants.sol";
import {BytesUtils} from "../lib/sgx_verifier_deployer/lib/automata-on-chain-pccs/src/utils/BytesUtils.sol";

contract DataFeedFeeder {
    IAutomataDcapAttestationFee public immutable sgx_quote_verifier;

    address immutable owner;

    mapping (string => DataFeedStorage) dataFeedStorages;
    uint constant PAIRS_AMOUNT = 7; // hardcoded pairs
    uint16 constant ENCLAVE_REPORT_OFFSET_OUTPUT = 13;
    uint16 constant MRENCLAVE_OFFSET = 64;
    uint16 constant REPORT_DATA_OFFSET = 320;
    bytes32 public mrEnclaveExpected = 0x4cb40e9053be3f8a7f54a5c46858fe44e37fc7fd66227b280a6f4b15afd947fd;

    constructor(
        IAutomataDcapAttestationFee _sgx_quote_verifier,
        string[PAIRS_AMOUNT] memory /* array size must be fixed in memory */ pair_names
    ) {
        sgx_quote_verifier = _sgx_quote_verifier;

        for (uint i = 0; i < pair_names.length; i++) {
            dataFeedStorages[pair_names[i]] = new DataFeedStorage(pair_names[i], 8 /* TODO hardcoded*/);
        }

        owner = msg.sender;
    }

    function mrEnclaveUpdate(bytes32 mrEnclaveNew) public {
        require (msg.sender == owner, "You are not contract owner");
        mrEnclaveExpected = mrEnclaveNew;
    }


    // ecnalveReport starts at ENCLAVE_REPORT_OFFSET_OUTPUT-th byte of the verification output
    function check_mrenclave(bytes memory verificationOutput) private view {
        bytes memory mrEnclaveReal = new bytes(32);
        for (uint i = 0; i < 32; i++) {
            // mrenclave starts at byte 64 of enclaveReport and is 32 bytes long
            // https://github.com/automata-network/automata-dcap-attestation/blob/3a854a31eb2345a31f9e33697eef0d814d031a12/evm/contracts/bases/QuoteVerifierBase.sol#L64-L76
            mrEnclaveReal[i] = verificationOutput[ENCLAVE_REPORT_OFFSET_OUTPUT + 64 + i];
        }
        require (bytes32(mrEnclaveReal) == mrEnclaveExpected, "mrEnclave from input differs from expected!");
    }

    function set_zk(
        string[PAIRS_AMOUNT] calldata pair_names,
        uint256[PAIRS_AMOUNT] calldata prices,
        uint256[PAIRS_AMOUNT] calldata timestamps,
        bytes calldata sgx_verification_journal,
        bytes calldata sgx_verification_seal
    ) external payable {

        (bool success, bytes memory output) = sgx_quote_verifier.verifyAndAttestWithZKProof{value: msg.value}(sgx_verification_journal, 1, sgx_verification_seal);
        if (!success) {
            // fail returns bytes(error_string)
            // success returns custom output type:
            // https://github.com/automata-network/automata-dcap-attestation/blob/b49a9f296a5e0cd8b1f076ec541b1239199cadd2/contracts/verifiers/V3QuoteVerifier.sol#L154
            require(success, string(output));
        }
        set(output, pair_names, prices, timestamps);
    }

    function set_onchain(
        string[PAIRS_AMOUNT] calldata pair_names,
        uint256[PAIRS_AMOUNT] calldata prices,
        uint256[PAIRS_AMOUNT] calldata timestamps,
        bytes calldata sgx_quote
    ) external payable {

        (bool success, bytes memory output) = sgx_quote_verifier.verifyAndAttestOnChain{value: msg.value}(sgx_quote);
        if (!success) {
            // fail returns bytes(error_string)
            // success returns custom output type:
            // https://github.com/automata-network/automata-dcap-attestation/blob/b49a9f296a5e0cd8b1f076ec541b1239199cadd2/contracts/verifiers/V3QuoteVerifier.sol#L154
            require(success, string(output));
        }
        set(output, pair_names, prices, timestamps);
    }

    function set(
        bytes memory output,
        string[PAIRS_AMOUNT] calldata pair_names,
        uint256[PAIRS_AMOUNT] calldata prices,
        uint256[PAIRS_AMOUNT] calldata timestamps
    ) internal {

        check_mrenclave(output);

        bytes32[] memory hashes = new bytes32[](PAIRS_AMOUNT * 3);

        for (uint256 i = 0; i < PAIRS_AMOUNT; i++) {
            hashes[i*3] = keccak256(abi.encodePacked(pair_names[i]));
            hashes[i*3 + 1] = keccak256(abi.encodePacked(prices[i]));
            hashes[i*3 + 2] = keccak256(abi.encodePacked(timestamps[i]));
        }
        bytes memory concatenated;

        for (uint256 i = 0; i < hashes.length; i++) {
            concatenated = abi.encodePacked(concatenated, hashes[i]);
        }

        bytes32 hashed_input_data = keccak256(concatenated);


        bytes memory data_hash_from_sgx = new bytes(32);
        for (uint i = 0; i < 32; i++) {
            data_hash_from_sgx[i] = output[ENCLAVE_REPORT_OFFSET_OUTPUT + REPORT_DATA_OFFSET + i];
        }
        require(hashed_input_data == bytes32(data_hash_from_sgx), "hashed_input_data != data_hash_from_sgx");

        // send round data to storage contracts
        for (uint i = 0; i < pair_names.length; i++) {
            dataFeedStorages[pair_names[i]].setNewRound(prices[i], timestamps[i]);
        }
    }

    function getPairStorageAddress(string memory pair_name) external view returns (address) {
        address result = address(dataFeedStorages[pair_name]);
        require(result != address(0), "There is no data for requested pair");
        return result;
    }
}
