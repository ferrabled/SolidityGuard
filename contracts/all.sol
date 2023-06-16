
/******************************** 

    REENTRANCY

******************************** */

// SPDX-License-Identifier: BSL-1.0 (Boost Software License 1.0)
pragma solidity > 0.8.13;

contract InsecureEtherVault {
    mapping (address => uint256) private userBalances;
    address private owner;

    function deposit() external payable {
        userBalances[msg.sender] += msg.value;
    }

    function withdrawAll() external {
        uint256 balance = getUserBalance(msg.sender);
        require(balance > 0, "Insufficient balance");

        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Failed to send Ether");

        userBalances[msg.sender] = 0;
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function getUserBalance(address _user) public view returns (uint256) {
        return userBalances[_user];
    }
}


pragma solidity > 0.8.13;
// Note: This is a rudimentary example, and mutexes are particularly 
//useful where there is substantial logic and/or shared state
contract SecureEtherVault {
    mapping (address => uint) private balances;
    bool private lockBalances;
    address private owner;


modifier nonReentrant {
        require(msg.sender == owner, "Must be owner");
        _;
    }

function deposit() payable public returns (bool) {
    require(!lockBalances);
    lockBalances = true;
    balances[msg.sender] += msg.value;
    lockBalances = false;
    return true;
}

function withdraw(uint amount) payable public returns (bool) {
    require(!lockBalances && amount > 0 && balances[msg.sender] >= amount);
    require(lockBalances);
    lockBalances = true;
    (bool success, ) = msg.sender.call{value:balances[msg.sender]}("");

    if (success) {
      balances[msg.sender] -= amount;
    }

    lockBalances = false;
    return true;
}

function withdrawAll() payable nonReentrant public {

    uint256 balance = balances[msg.sender];
    require(balance > 0, "Insufficient balance");

    (bool success, ) = msg.sender.call{value: balance}("");
    require(success, "Failed to send Ether");

    balances[msg.sender] = 0;
}
}

pragma solidity >=0.8.13 <=0.8.19;
contract SecureEtherVault2 {
    mapping (address => uint256) private userBalances;

    function deposit() external payable {
        userBalances[msg.sender] += msg.value;
    }

    function withdrawAll() external {
        uint256 balance = getUserBalance(msg.sender);
        require(balance > 0, "Insufficient balance");

        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Failed to send Ether");

        userBalances[msg.sender] = 0;
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function getUserBalance(address _user) public view returns (uint256) {
        return userBalances[_user];
    }
}



/******************************** 

    SELF DESTRUCT

******************************** */

pragma solidity ^0.8.17;

contract EtherGame {
    uint public targetAmount = 7 ether;
    address public winner;
    address private owner;

    modifier onlyOwner {
        require(msg.sender == owner, "Must be owner");
        _;
    }

    function deposit() public payable {
        require(msg.value == 1 ether, "You can only send 1 Ether");

        uint balance = address(this).balance;
        require(balance <= targetAmount, "Game is over");

        if (balance == targetAmount) {
            winner = msg.sender;
        }
    }

    function claimReward() public {
        require(msg.sender == winner, "Not winner");

        (bool sent, ) = msg.sender.call{value: address(this).balance}("");
        require(sent, "Failed to send Ether");
    }

    function attack(address payable receiver) public payable {
        require(msg.sender == owner);
        // You can simply break the game by sending ether so that
        // the game balance >= 7 ether

        // cast address to payable
        selfdestruct(receiver);
    }

    function attack2(address payable receiver) onlyOwner public payable {
        // You can simply break the game by sending ether so that
        // the game balance >= 7 ether

        // cast address to payable
        selfdestruct(receiver);
    }

       function attack3(address payable receiver) private {
        // You can simply break the game by sending ether so that
        // the game balance >= 7 ether

        // cast address to payable
        selfdestruct(receiver);
    }
}    


pragma solidity ^0.8.17;

// The goal of this game is to be the 7th player to deposit 1 Ether.
// Players can deposit only 1 Ether at a time.
// Winner will be able to withdraw all Ether.

/*
1. Deploy EtherGame
2. Players (say Alice and Bob) decides to play, deposits 1 Ether each.
2. Deploy Attack with address of EtherGame
3. Call Attack.attack sending 5 ether. This will break the game
   No one can become the winner.

What happened?
Attack forced the balance of EtherGame to equal 7 ether.
Now no one can deposit and the winner cannot be set.
*/

contract EtherGame2 {
    uint public targetAmount = 7 ether;
    address public winner;

    function deposit() public payable {
        require(msg.value == 1 ether, "You can only send 1 Ether");

        uint balance = address(this).balance;
        require(balance <= targetAmount, "Game is over");

        if (balance == targetAmount) {
            winner = msg.sender;
        }
    }

    function claimReward() public {
        require(msg.sender == winner, "Not winner");

        (bool sent, ) = msg.sender.call{value: address(this).balance}("");
        require(sent, "Failed to send Ether");
    }

    function attack(address payable receiver) public payable {
        // You can simply break the game by sending ether so that
        // the game balance >= 7 ether

        // cast address to payable
        selfdestruct(receiver);
    }
}    



/******************************** 

    DELEGATE CALL

******************************** */

pragma solidity > 0.8.13;
// compiler version must be greater than or equal to 0.8.17 and less than 0.9.0
contract FibonacciBalance {

    address public fibonacciLibrary;
    // the current Fibonacci number to withdraw
    uint public calculatedFibNumber;
    // the starting Fibonacci sequence number
    uint public start = 3;
    uint public withdrawalCounter;
    // the Fibonancci function selector
    bytes4 constant fibSig = bytes4(keccak256("setFibonacci(uint256)"));

    // constructor - loads the contract with ether
    constructor(address _fibonacciLibrary) payable {
        fibonacciLibrary = _fibonacciLibrary;
    }

    function withdraw() public payable{
        withdrawalCounter += 1;
        // this sets calculatedFibNumber
        fibonacciLibrary.delegatecall(abi.encode(fibSig, withdrawalCounter));
        payable(msg.sender).transfer(calculatedFibNumber * 1 ether);
    }

    // allow users to call Fibonacci library functions
    function pp() public {
        fibonacciLibrary.delegatecall(msg.data);
    }
}


pragma solidity ^0.8.17;
contract HackMe {
    address public lib;
    address public owner;
    uint public someNumber;

    constructor(address _lib) {
        lib = _lib;
        owner = msg.sender;
    }

    function doSomething(uint _num) public {
        lib.delegatecall(abi.encodeWithSignature("doSomething(uint256)", _num));
        address x = tx.origin;
        //function transfer
        payable(x).transfer(2);
        payable(x).send(2);

    }
}


/******************************** 

    UNCHECKED CALL

******************************** */

pragma solidity > 0.8.13;

contract Lotto {

    bool public payedOut = false;
    address payable public winner;
    uint public winAmount;

    function sendToWinnerVuln() public {
        require(!payedOut);
        winner.send(winAmount);
        payedOut = true;
    }

    function callVuln() public {
        msg.sender.call{value: winAmount}("");
    }

    function sendToWinner() public {
        require(!payedOut);
        (bool success) = winner.send(winAmount);
        payedOut = true;
    }

    function call() public {
        (bool success, ) = msg.sender.call{value: winAmount}("");
    }
}



/******************************** 

    OLD VERSIONS

******************************** */


pragma solidity > 0.7.1;

contract UncheckedMath {
    function nothing(uint x, uint y) external pure returns (uint) {
        // 22291 gas
        return 0;
    }
}


/******************************** 

    BLOCK TIMESTAMP

******************************** */


pragma solidity ^0.8.17;
contract Roulette {
    uint public pastBlockTime;

    constructor() payable {}

    function spin() external payable {
        require(msg.value == 10 ether); // must send 10 ether to play
        require(block.number != pastBlockTime); // only 1 transaction per block

        pastBlockTime = block.timestamp;

        if (block.number % 15 == 0) {
            (bool sent, ) = msg.sender.call{value: address(this).balance}("");
            require(sent, "Failed to send Ether");
        }
    }
}



/******************************** 

    TXORIGN USAGE

*********************************/

pragma solidity ^0.8.19;
contract TXOrigin {
    address public owner;

    constructor() payable {
        owner = msg.sender;
    }

    function transfer(address payable _to, uint _amount) public {
        require(tx.origin == owner, "Not owner");

        (bool sent, ) = _to.call{value: _amount}("");
        require(sent, "Failed to send Ether");
    }
}





/******************************** 

    UNCHECKED EXPRESSION

******************************** */

pragma solidity ^0.8.17;

contract UncheckedMaths {
    function add(uint x, uint y) external pure returns (uint) {
        unchecked {
            return x + y;
        }
    }

    function sub(uint x, uint y) external pure returns (uint) {
        unchecked {
            return x - y;
        }
    }

    function sumOfCubes(uint x, uint y) external pure returns (uint) {
        unchecked {
            uint x3 = x * x * x;
            uint y3 = y * y * y;

            return x3 + y3;
        }
    }
}


/******************************** 

DOS VULNERABLE AND NON VULNERABLE

******************************** */

pragma solidity ^0.8.17;

contract VulnDos {
    address[] private refundAddresses;
    mapping (address => uint) public refunds;

    // bad
    function refundAll() public {
        for(uint x; x < refundAddresses.length; x++) { // arbitrary length iteration based on how many addresses participated
            require(gasleft() > 1000);
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
        }
    }


    function refundAllRequire() public {
        uint x = 0;
        while(refundAddresses.length > 5) { // arbitrary length iteration based on how many addresses participated
            require(gasleft() > 1000);
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
            x++;
        }
    }


    function refundAll2() public {
        uint x = 0;
        require(gasleft() > 1000);
        while(refundAddresses.length > 5 && gasleft() > 1000) { // arbitrary length iteration based on how many addresses participated
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
            x++;
        }
    }
}


pragma solidity ^0.8.17;

contract NonVulnDos {
    address[] private refundAddresses;
    mapping (address => uint) public refunds;

    // bad
    function refundAll() public {
        for(uint x; x < refundAddresses.length; x++) { // arbitrary length iteration based on how many addresses participated
            require(gasleft() > 1000);
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
        }
    }


    function refundAllRequire() public {
        uint x = 0;
        while(refundAddresses.length > 5) { // arbitrary length iteration based on how many addresses participated
            require(gasleft() > 1000);
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
            x++;
        }
    }


    function refundAll2() public {
        uint x = 0;
        require(gasleft() > 1000);
        while(refundAddresses.length > 5 && gasleft() > 1000) { // arbitrary length iteration based on how many addresses participated
            require(payable(refundAddresses[x]).send(refunds[refundAddresses[x]])); // doubly bad, now a single failure on send will hold up all funds
            x++;
        }
    }
}


