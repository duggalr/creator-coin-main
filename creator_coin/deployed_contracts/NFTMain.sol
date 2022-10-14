// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "./contracts/token/ERC721/ERC721.sol";
import "./contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "./contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "./contracts/token/ERC721/extensions/ERC721Burnable.sol";
import "./contracts/access/Ownable.sol";
import "./contracts/utils/Counters.sol";



/// @custom:security-contact duggalr42@gmail.com
contract CreatorNFT is ERC721, ERC721Enumerable, ERC721URIStorage, ERC721Burnable, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;


    /// Main Public Key
    address private _platformAddress = 0x1CEE82EEd89Bd5Be5bf2507a92a755dcF1D8e8dc;
    uint256 private _platformFee = 3;

    /// Token Metadata
    uint256 private _maxTokenSupply;
    uint256 private _maxTokenPerSale;
    uint256 private _tokenPrice;  // will be in ETH denomination 
    string private _baseTokenURI;
    address private _deployerAddress;


    constructor(string memory tokenName, string memory tokenSymbol, uint256 totalSupply, uint256 maxNumPerSale, uint256 _userTokenPrice, string memory _userTokenURI) ERC721(tokenName, tokenSymbol) {

        require(maxNumPerSale > 0, "Max Token Per Sale must be >0.");
        require(totalSupply > 0, "Max Token Supply must be >0.");

        _maxTokenSupply = totalSupply;
        _maxTokenPerSale = maxNumPerSale;
        _tokenPrice = _userTokenPrice;
        _baseTokenURI = _userTokenURI;

        _deployerAddress = msg.sender;

    } 


    // TODO: 
      // add getter methods for all important metadata of nft-token

    function getTokenPrice() public view returns(uint256) {        
        return _tokenPrice;
    }


    function getMaxTokenSupply() public view returns (uint256) {
        return _maxTokenSupply;
    }


    function getCurrentTokenID() public view returns (uint256) {
        return _tokenIdCounter.current();
    }


    // TODO: add the for-loop and remove 'to'-addr; should be msg.sender only
    function safeMint(uint256 _numTokens) public payable {
      
        uint256 tokenId = _tokenIdCounter.current();
        require( _numTokens > 0 && _numTokens <= _maxTokenPerSale, "Amount of tokens exceeds amount of tokens you can purchase in a single purchase.");
        require(_maxTokenSupply >= tokenId + _numTokens, "Not enough tokens left to buy.");  // (tokenID+1) since tokenID starts at 0
        require(msg.value == _tokenPrice * _numTokens, "Amount of ether sent not correct.");  // require msg.value to be exactly correct


        // TODO: Re-entrancy attack? 
            // Call returns a boolean value indicating success or failure.
            // This is the current recommended method to use.

        // TODO: what if malicious user has set $0 price for token? 

        uint256 _platformCost = (_platformFee * msg.value) / 100;
        uint256 _remainingValue = msg.value - _platformCost;

        (bool platformSent, bytes memory platformData) = _platformAddress.call{value: _platformCost}("");  // send to platform
        require(platformSent, "Failed to send Ether");

        (bool sent, bytes memory data) = _deployerAddress.call{value: _remainingValue}("");  // sent to creator
        require(sent, "Failed to send Ether");

        // Loop to mint amount requested
        for(uint256 i = 0; i < _numTokens; i++) {
            _safeMint(msg.sender, _tokenIdCounter.current());
            _setTokenURI(_tokenIdCounter.current(), _baseTokenURI);
            _tokenIdCounter.increment();
        }

        // _tokenIdCounter.increment();
        // _safeMint(to, tokenId);
        // _setTokenURI(tokenId, _baseTokenURI);
 
    }


    // Callable by owner to increase supply
    function increaseTokenSupply(uint256 newSupply) public onlyOwner {

        require(newSupply > 0 && newSupply > _maxTokenSupply, "Max Token Supply must be >0 and greater than previous maxTokenSupply.");

        _maxTokenSupply = newSupply;

    }


    // The following functions are overrides required by Solidity.

    function _beforeTokenTransfer(address from, address to, uint256 tokenId)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._beforeTokenTransfer(from, to, tokenId);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
}





