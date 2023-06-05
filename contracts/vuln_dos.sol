// SPDX-License-Identifier: MIT 
pragma solidity ^0.8.17;

contract VulnDos {
    address[] private refundAddresses;
    mapping (address => uint) public refunds;
    event RefundAll(uint count);

    // bad
    function refundAll() public {
        emit RefundAll(refundAddresses.length);
        for(uint x; x < refundAddresses.length; x++) { // arbitrary length iteration based on how many addresses participated
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
        }
    }

    // bad
    function refundAll2() public {
        emit RefundAll(refundAddresses.length);
        uint x = 0;
        while(refundAddresses.length > 5) { // arbitrary length iteration based on how many addresses participated
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
            x++;
        }
    }
}