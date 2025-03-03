// Copyright 2024 Diffuse
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

struct RoundData {
    int256 answer;
    uint256 timestamp;
}

contract DataFeedStorage {

    uint16 constant public ROUNDS_STORAGE_SIZE = 256;
    uint8 immutable public decimals;
    uint80 roundsAmount = 0;
    address public owner;
    string public description;
    RoundData[ROUNDS_STORAGE_SIZE] roundDataArray;

    constructor (string memory _description_string, uint8 _decimals_amount) {
        description = _description_string;
        decimals = _decimals_amount;
        owner = msg.sender;
    }

    event NewRoundEvent(uint256 roundId);

    function transferOwnership(address newOwner) public {
        require(msg.sender == owner, "Only storage owner can transfer ownership");
        owner = newOwner;
    }

	function latestAnswer() external view returns (int256) {
        uint80 _latestRound = latestRound();
        return roundDataArray[_latestRound % ROUNDS_STORAGE_SIZE].answer;
    }

	function latestRound() public view returns (uint80) {
        require(roundsAmount != 0, "there has been no rounds yet");
        uint80 _latestRound = roundsAmount - 1;
        return _latestRound;
    }

	function roundToIndex(uint80 _roundId) internal view returns (uint80) {
        require(_roundId < roundsAmount, "_roundId must be less than roundsAmount");
        if (roundsAmount >= ROUNDS_STORAGE_SIZE) {
            require(_roundId >= roundsAmount - ROUNDS_STORAGE_SIZE, "contract stores only ROUNDS_STORAGE_SIZE latest rounds");
        }
        return _roundId % ROUNDS_STORAGE_SIZE;
    }

	function getRoundData(uint80 _roundId) external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound) {
        uint80 index = roundToIndex(_roundId);
        int256 _answer = roundDataArray[index].answer;
        uint256 _timestamp = roundDataArray[index].timestamp;

        return (_roundId, _answer, _timestamp, _timestamp, _roundId);
    }

	function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound) {
        uint80 _latestRound = latestRound();
        uint80 _latestIndex = roundToIndex(_latestRound);
        int256 _answer = roundDataArray[_latestIndex].answer;
        uint256 _timestamp = roundDataArray[_latestIndex].timestamp;

        return (_latestRound, _answer, _timestamp, _timestamp, _latestRound);
    }

    function setNewRound(int256 answer, uint256 timestamp) public {
        require(msg.sender == owner, "Only storage owner can add new data");
        emit NewRoundEvent(roundsAmount);
        roundsAmount = roundsAmount + 1;
        uint80 _latestIndex = roundToIndex(latestRound());
        roundDataArray[_latestIndex] = RoundData(answer, timestamp);
    }
}
