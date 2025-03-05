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

contract DataFeedFeeder {
    IAutomataDcapAttestationFee public sgxQuoteVerifier;

    address public dataFeedProxyAddress;

    address public immutable owner;

    mapping (string => DataFeedStorage) public dataFeedStorages;

    uint16 constant ENCLAVE_REPORT_OFFSET_OUTPUT = 13;
    uint16 constant MRENCLAVE_OFFSET = 64;
    uint16 constant REPORT_DATA_OFFSET = 320;
    bytes32 public mrEnclaveExpected = 0x4cb40e9053be3f8a7f54a5c46858fe44e37fc7fd66227b280a6f4b15afd947fd;

    constructor(
        IAutomataDcapAttestationFee _sgxQuoteVerifier
    ) {
        sgxQuoteVerifier = _sgxQuoteVerifier;
        owner = msg.sender;
    }

    function mrEnclaveUpdate(bytes32 mrEnclaveNew) external {
        require (msg.sender == owner, "only contract owner can call mrEnclaveUpdate");
        mrEnclaveExpected = mrEnclaveNew;
    }

    function quoteVerifierUpdate(address newQuoteVerifierAddress) external {
        require (msg.sender == owner, "only contract owner can call quoteVerifierUpdate");
        sgxQuoteVerifier = IAutomataDcapAttestationFee(newQuoteVerifierAddress);
    }

    function transferStorage(string calldata pair_name, address newFeederAddress) external {
        require (msg.sender == owner, "only contract owner can call transferStorage");
        DataFeedFeeder(newFeederAddress).setExistingPair(pair_name, address(dataFeedStorages[pair_name]));
        dataFeedStorages[pair_name].transferOwnership(newFeederAddress);
    }

    function setProxy(address proxyAddress) external {
        require (msg.sender == owner, "only contract owner can call setProxy");
        dataFeedProxyAddress = proxyAddress;
    }

    // enclaveReport starts at ENCLAVE_REPORT_OFFSET_OUTPUT-th byte of the verification output
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
        string[] calldata pair_names,
        uint128[] calldata prices,
        uint128[] calldata timestamps,
        bytes calldata sgx_verification_journal,
        bytes calldata sgx_verification_seal
    ) external payable {

        (bool success, bytes memory output) = sgxQuoteVerifier.verifyAndAttestWithZKProof{value: msg.value}(sgx_verification_journal, 1, sgx_verification_seal);
        if (!success) {
            // fail returns bytes(error_string)
            // success returns custom output type:
            // https://github.com/automata-network/automata-dcap-attestation/blob/b49a9f296a5e0cd8b1f076ec541b1239199cadd2/contracts/verifiers/V3QuoteVerifier.sol#L154
            require(success, string(output));
        }
        set(output, pair_names, prices, timestamps);
    }

    function set_onchain(
        string[] calldata pair_names,
        uint128[] calldata prices,
        uint128[] calldata timestamps,
        bytes calldata sgx_quote
    ) external payable {

        (bool success, bytes memory output) = sgxQuoteVerifier.verifyAndAttestOnChain{value: msg.value}(sgx_quote);
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
        string[] calldata pair_names,
        uint128[] calldata prices,
        uint128[] calldata timestamps
    ) internal {

        check_mrenclave(output);

        require (pair_names.length == prices.length, "pair_names and prices length mismatch");
        require (prices.length == timestamps.length, "prices and timestamps length mismatch");

        bytes32[] memory hashes = new bytes32[](pair_names.length * 3);

        for (uint128 i = 0; i < pair_names.length; i++) {
            hashes[i*3] = keccak256(abi.encodePacked(pair_names[i]));
            hashes[i*3 + 1] = keccak256(abi.encodePacked(uint256(prices[i])));
            hashes[i*3 + 2] = keccak256(abi.encodePacked(uint256(timestamps[i])));
        }
        bytes memory concatenated;

        for (uint128 i = 0; i < hashes.length; i++) {
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
            require (
                address(dataFeedStorages[pair_names[i]]) != address(0),
                string(abi.encodePacked("storage for pair ", pair_names[i], " is not deployed yet"))
            );
            dataFeedStorages[pair_names[i]].setNewRound(int128(prices[i]), timestamps[i]);
        }
    }

    function setNewPair(string calldata pair_name) external returns (address) {
        require(address(dataFeedStorages[pair_name]) == address(0), "Storage is already deployed for requested pair");
        DataFeedStorage newStorage = new DataFeedStorage(pair_name, 8 /* TODO hardcoded*/);
        dataFeedStorages[pair_name] = newStorage;
        return address(newStorage);
    }

    function setExistingPair(string calldata pairName, address pairAddr) external {
        require(address(dataFeedStorages[pairName]) == address(0), "Storage is already deployed for requested pair");
        dataFeedStorages[pairName] = DataFeedStorage(pairAddr);
    }

    function getPairStorageAddress(string calldata pair_name) external view returns (address) {
        address result = address(dataFeedStorages[pair_name]);
        require(result != address(0), "There is no data for requested pair");
        return result;
    }
}
