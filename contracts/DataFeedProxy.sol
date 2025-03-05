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

pragma solidity 0.8.20;

interface IStoragesGetter {
    function getPairStorageAddress(string calldata pair_name) external view returns (address);
}

contract DataFeedProxy {

    address public immutable owner;
    address public feeder;

    constructor() {
        owner = tx.origin;
    }


    function updateFeeder(address _feeder) external {
        require(msg.sender == owner, "only owner can call updateFeeder");
        feeder = _feeder;
    }

    function getPairStorageAddress(string calldata pair_name) external view returns (address) {
        IStoragesGetter dataFeedFeeder =  IStoragesGetter(feeder);
        return dataFeedFeeder.getPairStorageAddress(pair_name);
    }
}
