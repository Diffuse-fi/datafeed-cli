// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/DataFeedFeeder.sol";
import "../contracts/IAutomataDcapAttestationFee.sol";

contract TestFeeder is Test {
    DataFeedFeeder feeder = new DataFeedFeeder();


    function setUpFeeder() public {
        feeder = new DataFeedFeeder();
    }

    function testSetNewPair() public {
        feeder.setNewPair("pair1");
    }

    function testSetNewPair2() public {
        feeder.setNewPair("pair1");
        feeder.setNewPair("pair2");
    }

    function testSetNewPairRevert() public {
        feeder.setNewPair("pair1");
        vm.expectRevert("Storage is already deployed for requested pair");
        feeder.setNewPair("pair1");
    }

    function testTransferStorage() public {
        feeder.setNewPair("pair1");

        DataFeedFeeder newFeeder = new DataFeedFeeder();
        feeder.transferStorage("pair1", address(newFeeder));
    }

}
