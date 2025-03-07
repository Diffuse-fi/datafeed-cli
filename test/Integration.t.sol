// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;


import "forge-std/Test.sol";
import "../contracts/DataFeedFeeder.sol";
import "../contracts/DataFeedStorage.sol";
import "../contracts/DataFeedProxy.sol";
import "../contracts/IAutomataDcapAttestationFee.sol";

contract TestIntegration is Test {
    IAutomataDcapAttestationFee public DummyVerifier;
    DataFeedProxy proxy = new DataFeedProxy();
    DataFeedFeeder oldFeeder = new DataFeedFeeder(DummyVerifier);
    DataFeedFeeder newFeeder = new DataFeedFeeder(DummyVerifier);

    function testTransfer() public {
        proxy.updateFeeder(address(oldFeeder));
    }

    function testTransfer2() public {
        oldFeeder.setProxy(address(proxy));
        proxy.updateFeeder(address(oldFeeder));
        assertEq(proxy.feeder(), address(oldFeeder));
        assertEq(address(oldFeeder.dataFeedProxyAddress()), address(proxy));
    }

    function testTransfer3() public {
        oldFeeder.setProxy(address(proxy));
        proxy.updateFeeder(address(oldFeeder));

        proxy.updateFeeder(address(newFeeder));
        newFeeder.setProxy(address(proxy));
        assertEq(proxy.feeder(), address(newFeeder));
        assertEq(newFeeder.dataFeedProxyAddress(), address(proxy));
    }

    function testStorageAddr() public {
        proxy.updateFeeder(address(oldFeeder));

        address addrFeeder = oldFeeder.setNewPair("pair1");
        address addrProxy = proxy.getPairStorageAddress("pair1");
        assertEq(addrFeeder, addrProxy);

        proxy.updateFeeder(address(newFeeder));
        oldFeeder.transferStorage("pair1", address(newFeeder));
        addrFeeder = newFeeder.getPairStorageAddress("pair1");
        addrProxy = proxy.getPairStorageAddress("pair1");
        assertEq(addrFeeder, addrProxy);
    }

}
