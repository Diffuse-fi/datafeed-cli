// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/DataFeedProxy.sol";

contract TestDataFeedProxy is Test {
    DataFeedProxy public dataFeedProxy;

    function setUp() public {
        dataFeedProxy = new DataFeedProxy();
    }

    function testGetPairsList() public {
        string[] memory res = dataFeedProxy.getPairsList();
        assertEq(res.length, 0);
    }

    function testSetPair() public {
        dataFeedProxy.setPair("asdf");
        string[] memory res = dataFeedProxy.getPairsList();
        assertEq(res.length, 1);
        assertEq(res[0], "asdf");
    }

    function testSetPair2() public {
        dataFeedProxy.setPair("asdf");
        dataFeedProxy.setPair("qwer");
        string[] memory res = dataFeedProxy.getPairsList();
        assertEq(res.length, 2);
        assertEq(res[0], "asdf");
        assertEq(res[1], "qwer");
    }

    function testSetPair3() public {
        dataFeedProxy.setPair("asdf");
        dataFeedProxy.setPair("qwer");
        dataFeedProxy.setPair("asdf");
        string[] memory res = dataFeedProxy.getPairsList();
        assertEq(res.length, 2);
        assertEq(res[0], "asdf");
        assertEq(res[1], "qwer");
    }

}
