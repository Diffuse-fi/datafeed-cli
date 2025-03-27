// Copyright 2024 RISC Zero, Inc.
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

pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import "forge-std/Test.sol";

import {DataFeedFeeder} from "../contracts/DataFeedFeeder.sol";

/// @notice Deployment script for the diffuse datafeed contracts.
/// @dev Use the following environment variable to control the deployment:
///     * Set one of these two environment variables to control the deployment wallet:
///         * PRIVATE_KEY private key of the wallet account.
///         * ETH_WALLET_ADDRESS address of the wallet account.
///
/// See the Foundry documentation for more information about Solidity scripts,
/// including information about wallet options.
///
/// https://book.getfoundry.sh/tutorials/solidity-scripting
/// https://book.getfoundry.sh/reference/forge/forge-script
contract DataFeedFeederDeploy is Script {

    function run() external {
        // Read and log the chainID
        uint256 chainId = block.chainid;
        console2.log("You are deploying on ChainID %d", chainId);

        // Determine the wallet to send transactions from.
        uint256 deployerKey = uint256(vm.envOr("ETH_WALLET_PRIVATE_KEY", bytes32(0)));
        address deployerAddr = address(0);
        if (deployerKey != 0) {
            // Check for conflicts in how the two environment variables are set.
            address envAddr = vm.envOr("ETH_WALLET_ADDRESS", address(0));
            require(
                envAddr == address(0) || envAddr == vm.addr(deployerKey),
                "conflicting settings from ETH_WALLET_PRIVATE_KEY and ETH_WALLET_ADDRESS"
            );

            vm.startBroadcast(deployerKey);
        } else {
            deployerAddr = vm.envAddress("ETH_WALLET_ADDRESS");
            vm.startBroadcast(deployerAddr);
        }


        // Deploy the application contract.
        DataFeedFeeder dataFeedFeeder = new DataFeedFeeder();
        console2.log("Deployed DataFeedFeeder to", address(dataFeedFeeder));

        vm.stopBroadcast();
    }
}
