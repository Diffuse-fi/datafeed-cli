// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/DataFeedStorage.sol";

contract TestDataFeedStorage is Test {
    DataFeedStorage public dataFeedStorage;
    string DESC = "asdf";
    uint8 DECIMALS = 8;

    function setUp() public {
        dataFeedStorage = new DataFeedStorage(DESC, DECIMALS);
    }

    function testDescription() public view {
        string memory result = dataFeedStorage.description();
        assertEq(result, DESC);
    }

    function testDecimals() public view {
        uint8 result = dataFeedStorage.decimals();
        assertEq(result, DECIMALS);
    }

    function testLatestRoundData() public {
        vm.expectRevert("there has been no rounds yet");
        dataFeedStorage.latestRoundData();
    }

    function testGetRoundData() public {
        vm.expectRevert("_roundId must be less than roundsAmount");
        dataFeedStorage.getRoundData(0);
    }

    function testSetNewRound() public {
        dataFeedStorage.setNewRound(1, 2);
    }

    function testSetGet1() public {
        dataFeedStorage.setNewRound(10, 100);
        (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)  = dataFeedStorage.latestRoundData();
        assertEq(roundId, 0);
        assertEq(answer, 10);
        assertEq(startedAt, 100);
        assertEq(updatedAt, 100);
        assertEq(answeredInRound, 0);
    }

    function testSetGet2() public {
        dataFeedStorage.setNewRound(10, 100);
        dataFeedStorage.setNewRound(20, 200);
        (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)  = dataFeedStorage.latestRoundData();
        assertEq(roundId, 1);
        assertEq(answer, 20);
        assertEq(startedAt, 200);
        assertEq(updatedAt, 200);
        assertEq(answeredInRound, 1);
    }

    function testLatestRoundData2() public {
        vm.expectRevert("there has been no rounds yet");
        dataFeedStorage.latestRoundData();
    }

    function testStorageRewriteLatestRoundData() public {
        uint80 LATEST = dataFeedStorage.ROUNDS_STORAGE_SIZE() + 10;

        for (uint128 i = 0; i < LATEST + 1; i++) {
            dataFeedStorage.setNewRound(int128(i), i*10);
        }
        (uint80 roundId, int256 answer, uint256 startedAt,,) = dataFeedStorage.getRoundData(LATEST);
        assertEq(roundId, LATEST);
        assertEq(uint256(answer), uint256(LATEST));
        assertEq(startedAt, 10*(LATEST));
    }

    function testStorageRewriteLatest() public {
        uint80 LATEST = dataFeedStorage.ROUNDS_STORAGE_SIZE() + 10;

        for (uint128 i = 0; i < LATEST + 1; i++) {
            dataFeedStorage.setNewRound(int128(i), i*10);
        }
        (uint80 roundId, int256 answer, uint256 startedAt,,) = dataFeedStorage.getRoundData(LATEST);
        assertEq(roundId, LATEST);
        assertEq(uint256(answer), uint256(LATEST));
        assertEq(startedAt, 10*(LATEST));
    }

    function testStorageRewriteOldest() public {
        uint80 LATEST = dataFeedStorage.ROUNDS_STORAGE_SIZE() + 10;
        uint80 TOO_SMALL = LATEST - dataFeedStorage.ROUNDS_STORAGE_SIZE();
        uint80 OLDEST = TOO_SMALL + 1;

        for (uint128 i = 0; i < LATEST + 1; i++) {
            dataFeedStorage.setNewRound(int128(i), i*10);
        }
        (uint80 roundId, int256 answer, uint256 startedAt,,) = dataFeedStorage.getRoundData(OLDEST);
        assertEq(roundId, OLDEST);
        assertEq(uint256(answer), uint256(OLDEST));
        assertEq(startedAt, 10*(OLDEST));
    }

    function testStorageRewriteTooBig() public {
        uint80 LATEST = dataFeedStorage.ROUNDS_STORAGE_SIZE() + 10;
        uint80 TOO_BIG = LATEST + 1;

        for (uint128 i = 0; i < LATEST + 1; i++) {
            dataFeedStorage.setNewRound(int128(i), i*10);
        }
        vm.expectRevert("_roundId must be less than roundsAmount");
        dataFeedStorage.getRoundData(TOO_BIG);
    }

    function testStorageRewriteTooSmall() public {
        uint80 LATEST = dataFeedStorage.ROUNDS_STORAGE_SIZE() + 10;
        uint80 TOO_SMALL = LATEST - dataFeedStorage.ROUNDS_STORAGE_SIZE();

        for (uint128 i = 0; i < LATEST + 1; i++) {
            dataFeedStorage.setNewRound(int128(i), i*10);
        }
        vm.expectRevert("contract stores only ROUNDS_STORAGE_SIZE latest rounds");
        dataFeedStorage.getRoundData(TOO_SMALL);
    }
}
