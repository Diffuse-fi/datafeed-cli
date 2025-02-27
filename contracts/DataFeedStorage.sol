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

    uint8 decimals_amount;
    string description_string;
    RoundData[] public roundDataArray;
    address public owner;

    constructor (string memory _description_string, uint8 _decimals_amount) {
        description_string = _description_string;
        decimals_amount = _decimals_amount;
        owner = msg.sender;
    }

    event NewRoundEvent(uint256 roundId);

    function transferOwnership(address newOwner) public {
        require(msg.sender == owner, "Only storage owner can transfer ownership");
        owner = newOwner;
    }

	function decimals() external view returns (uint8) {
        return decimals_amount;
    }

	function description() external view returns (string memory) {
        return description_string;
    }

	function latestAnswer() external view returns (int256) {
        require(roundDataArray.length != 0, "there has been no rounds yet");
        return roundDataArray[roundDataArray.length - 1].answer;
    }

	function latestRound() external view returns (uint256) {
        require(roundDataArray.length != 0, "there has been no rounds yet");
        uint80 _latest_round = uint80(roundDataArray.length - 1);
        return _latest_round;
    }

	function getRoundData(uint80 _roundId) external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound) {
        require(roundDataArray.length != 0, "there has been no rounds yet");
        int256 _answer = roundDataArray[_roundId].answer;
        uint256 _timestamp = roundDataArray[_roundId].timestamp;
        uint80 latest_round = uint80(roundDataArray.length - 1);

        return (_roundId, _answer, _timestamp, _timestamp, latest_round);
    }

	function latestRoundData() external view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound) {
        require(roundDataArray.length != 0, "there has been no rounds yet");
        uint80 _latest_round = uint80(roundDataArray.length - 1);
        int256 _answer = roundDataArray[_latest_round].answer;
        uint256 _timestamp = roundDataArray[_latest_round].timestamp;

        return (_latest_round, _answer, _timestamp, _timestamp, _latest_round);
    }

    function setNewRound(int256 answer, uint256 timestamp) public {
        require(msg.sender == owner, "Only storage owner can add new data");
        roundDataArray.push(RoundData(answer, timestamp));
        emit NewRoundEvent(roundDataArray.length - 1);
    }
}
