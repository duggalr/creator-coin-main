const API_HOST = 'http://127.0.0.1:7500/'

let ethersProvider;


if (window.ethereum){
  
  // TODO: 
    // 'any' refers to any network 
    // will this approach mess up the code below?
  ethersProvider = new ethers.providers.Web3Provider(window.ethereum, 'any');

}

 
// let web3;
// let user_account_pk_address;

let loginErrorModal;
let loginErrorTwoModal;

var loginModalExists = document.getElementById("loginErrorOne");
if (loginModalExists != null){
  loginErrorModal = new bootstrap.Modal('#loginErrorOne')
  loginErrorTwoModal = new bootstrap.Modal('#loginErrorTwo')
}



// Much of the metamask login is based from:
  // https://github.com/ManaanAnsari/MetaMask-Login-Python

  
const detectCurrentProvider = () => {
  let provider;

  if (window.ethereum && window.ethereum.isMetaMask) {
    provider = window.ethereum;
    // TODO: only this one will work <-- test this code on Brave, Chrome, Safari, Firefox, Opera
    return provider;

  } else {

    loginErrorModal.show();

  }

  // else if (window.web3) {
  //   provider = window.web3.currentProvider;
  // }    
  
  // } else {
  
  //   // alert(
  //   //   "Metamask is not installed! Please install the metamask extension and try again! Thank you."
  //   //   // "Only Metamask wallet supported! Please use a Metamask supported browser (Chrome, Firefox, Brave)."
  //   // )

  //   // console.log('my-modal:', myModal);
  // // myModal.show();

  //   loginErrorModal.show();

  // }

};



const onConnect = async () => {

  // const currentProvider = detectCurrentProvider();
  
  // const message = 'Very Message Such Wow';
  // // const msg = `0x${bops.from(message, 'utf8').toString('hex')}`;

  // await currentProvider.request({ method: 'eth_requestAccounts' });
  // let web3 = new Web3(currentProvider);
  // const userAccount = await web3.eth.getAccounts();

  // // console.log('ua:', userAccount)

  // const sign = await currentProvider.request({
  //   method: 'personal_sign',
  //   params: [message, userAccount[0]],
  // });


  try {
    const currentProvider = detectCurrentProvider();

    if (currentProvider) {
      // if (currentProvider !== window.ethereum) {
      //   // alert.log(
      //   //   'Only Metamask wallet supported! Please use a Metamask supported browser (Chrome, Firefox, Brave).'
      //   // );
      //   loginErrorModal.show();
      // }

      ethersProvider = new ethers.providers.Web3Provider(window.ethereum, 'any');

      const walletUnlocked =  await currentProvider._metamask.isUnlocked();
      // console.log('is-unlocked:', walletUnlocked );

      if (walletUnlocked === true){

        await currentProvider.request({ method: 'eth_requestAccounts' });
        let web3 = new Web3(currentProvider);
  
        // const userAccount = await web3.eth.getAccounts();
        // console.log('user-account:', userAccount);
        // const balance = await web3.eth.getBalance(userAccount[0]);
        // console.log('balance:', balance);
  
        // userAccount will be length 1 (if user has account)
          // if multiple different accounts, user can connect through Metamask and it wil show 
          // the current, connected public-key (<-- will be a separate user in our app)
        const userAccount = await web3.eth.getAccounts();
        // const user_account_pk_address = userAccount[0];
        let user_account_pk_address = userAccount[0];

        // console.log('user-pk:', user_account_pk_address);
        
        var apiURL = new URL(API_HOST + 'generate_nonce?');
        apiURL.searchParams.append('web3_address', user_account_pk_address);
        // console.log('api-url:', apiURL)
        const user_nonce_res = await axios.get(apiURL.href)
        
        if (user_nonce_res.status == 200){
          const user_nonce = user_nonce_res['data']['data']['nonce']
          
          let signature = null;
          
          try{
            // signature = await web3.eth.sign( web3.utils.sha3(user_nonce), user_account_pk_address )

            // TODO: is personal_sign safe? 

            // console.log('user-nonce: ' + user_nonce + ' user-pk: ' + user_account_pk_address);

            var message = "\nBy signing this message, you will sign the randomly generated nonce.  \n\nNonce: " + user_nonce + " \n\nWallet Address: " + user_account_pk_address
            signature = await currentProvider.request({
              method: 'personal_sign',
              params: [ message, user_account_pk_address ],
              // params: [user_account_pk_address, message],
              // from: user_account_pk_address
            });
 
          } catch(e){
            // console.log("signature-error:", e)
            alert("MetaMask Signature Denied.")

          }
    
          if (signature){
    
            const data = {
              pk_address: user_account_pk_address,
              nonce_signature: signature,
            };
            
            axios.post(API_HOST + "login/", data).then((response) => {
              
              if(response.status == 200){
                console.log("res-data:", response);
  
                if (response['data']['success'] === true){
                  // var profile_url = {% url 'user_profile' %};
                  window.location.href = 'http://127.0.0.1:7500/profile/' + response['data']['profile_id'];  // TODO: redirect to profile?
                  // window.location.reload();
                }
  
                // let access_token = "token " + response.data.user_token
                // window.sessionStorage.setItem("user_obj", JSON.stringify(response.data.user_data));
                // window.sessionStorage.setItem("access_token", access_token);
                // window.location.reload();
  
              } else{ // TODO: test to see if we can provide more specific message for user here
                alert("Login Failed... Please try again!")
              }
  
            })
  
          }
  
        }

      } else { // wallet is not unlocked

        loginErrorTwoModal.show();
        
      }

    }

  } catch (err) {

    loginErrorModal.show();

    // alert("There was an error fetching your Metamask Account. Are you sure you are logged in to Metamask? Try to confirm if you are logged in, and try again!")

    // console.log('error:', err)
    // console.log(
    //   'There was an error fetching your accounts. Make sure your Ethereum client is configured correctly.'
    // );

  }
  
};
 



const getBalance = async () => {

  const currentProvider = detectCurrentProvider();
  await currentProvider.request({ method: 'eth_requestAccounts' });
  web3 = new Web3(currentProvider);

  // const userAccount = await web3.eth.getAccounts();
  // console.log('user-account:', userAccount);
  // const balance = await web3.eth.getBalance(userAccount[0]);
  // console.log('balance:', balance);

  // userAccount will be length 1 (if user has account)
    // if multiple different accounts, user can connect through Metamask and it wil show 
    // the current, connected public-key (<-- will be a separate user in our app)
  const userAccount = await web3.eth.getAccounts();
  // const user_account_pk_address = userAccount[0];
  var user_account_pk_address = userAccount[0];

  console.log('user-pk:', user_account_pk_address);

  const currentBalance = await web3.eth.getBalance(user_account_pk_address);
  console.log('current-balance:', currentBalance);
  
  // var to_pk_address = "0x9d225E305758483AdD2A372B444acda6c0c21Fb1";
  var to_pk_address = "0x2DE45cAF766F37D5569E27566ffd18dd160Ceb05";

  // TODO:
    // make AJAX call to ensure current 'buyer' has an account and is logged in
      // once verified, also return the nft price and nft owner pk address 
        // Steps:
          // execute ETH transfer 
          // execute smart-contract function to mint new NFT and transfer to specific user

  var eth_amount = "4";
  var wei_eth_amount = "0x" + Number(Web3.utils.toWei(eth_amount, "ether")).toString(16);

  console.log('total amount in wei:', wei_eth_amount);
  
  const transactionParameters = {
    from: user_account_pk_address, // must match user's active address.
    to: to_pk_address, // Required except during contract publications.
    value: wei_eth_amount, // Only required to send ether to the recipient from the initiating external account.    
  };

  const txHash = await ethereum.request({
    method: 'eth_sendTransaction',
    params: [transactionParameters],
  });

  console.log('tx-hash:', txHash);


}

// var myContract = new web3.eth.Contract('0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab');





function deployToken(){

  $.ajax({
    type: 'POST',
    url: "{% url 'deploy_new_nft' %}",
    data: serializedData,
    success: function (response) {
      console.log('res:', response);
    }
  })

  
}



// function emailBetaSubmit(e){

//   e.preventDefault();

//   $.ajax({
//     type: 'POST',
//     url: "{% url 'home' %}",
//     data: {
//       'user_email': $('#user_email_value').val()
//     },
//     success: function (response) {
//       console.log('res:', response);
//     }
//   })

// }








function getContractABI(){

  return new Promise( function(resolve, reject){

    $.getJSON(contract_fp, function(data) {
      // console.log('json-data:', data)
      resolve(data);
    });

  })

}



const mintToken = async () => {  

  const currentProvider = detectCurrentProvider();
  await currentProvider.request({ method: 'eth_requestAccounts' });
  web3 = new Web3(currentProvider);

  const userAccount = await web3.eth.getAccounts();
  var user_account_pk_address = userAccount[0];

  const currentBalance = await web3.eth.getBalance(user_account_pk_address);
  console.log('current-balance:', currentBalance);

  const contractAddress = "0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B";
  
  // console.log('contract-fp:', contract_fp);
  var contract_abi = await getContractABI();
  var myContract = new web3.eth.Contract(contract_abi, contractAddress,
    {
      from: '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1', // default from address
    }
  );
  // console.log('my-contract:', myContract)
  // console.log('methods:', myContract.methods);
  
  myContract.methods.safeMint("0xa160F6b9Cb594906a601c551c25C501DdAb5107A").send();
  // TODO: 
    // how to 'lazy-mint' or in other words, allow minting when original creator is not signed in <-- solve this, then below
      // make myself the owner? but, I can't sign every transaction; how to do this automatically?
      // see the online guides 

    // shouldn't the price be checked in the contract? for minting and transfer
    // **what's to prevent someone from transferring nft's to another account? (without original owners permission)

    


//   var myContract = new web3.eth.Contract([...], '0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe', {
//     from: '0x1234567890123456789012345678901234567891', // default from address
//     gasPrice: '20000000000' // default gas price in wei, 20 gwei in this case
// });




  // // TODO: interact with contract via AJAX <-- should be on server-side as this is safest

  // axios.post(API_HOST + "login", data).then((response) => {
            
  //   if(response.status == 200){
  //     console.log("res-data:", response);

  //     if (response['data']['success'] === true){
  //       // var profile_url = {% url 'user_profile' %};
  //       window.location.href = 'http://127.0.0.1:7500/profile/' + response['data']['profile_id'];  // TODO: redirect to profile?
  //       // window.location.reload();
  //     }

  //     // let access_token = "token " + response.data.user_token
  //     // window.sessionStorage.setItem("user_obj", JSON.stringify(response.data.user_data));
  //     // window.sessionStorage.setItem("access_token", access_token);
  //     // window.location.reload();

  //   } else{ // TODO: test to see if we can provide more specific message for user here
  //     alert("Login Failed... Please try again!")
  //   }

  // })

  


}


// call from web-app, not from sep script



function handleAccountChange(){

  return new Promise(function(){
    
    // fetch metadata (ajax-request)
    fetch(API_HOST + "handle-account-change/")
    .then(response => response.json())
    .then(json => {

      if (json['redirect'] === true){
        window.location.href = 'http://127.0.0.1:7500/logout'
      }

    })

  })

}



if (window.ethereum){

  window.ethereum.on('accountsChanged', (accounts) => {
    // Handle the new accounts, or lack thereof.
    // "accounts" will always be an array, but it can be empty.
    console.log('account-changed:', accounts);
    // if (accounts.length > 0) {
    //   var current_account = accounts[0]
    // }

    handleAccountChange();
  
  });
  
}



// TODO: handle the event changes (do chain-change on token buy/deploy)
// currentProvider.on('chainChanged', (chainId) => {
//   // Handle the new chain.
//   // Correctly handling chain changes can be complicated.
//   // We recommend reloading the page unless you have good reason not to.
//   // window.location.reload();

//   console.log('chain-changed:', chainId);

// });





const testOne = async () => {  

  const transactionParameters = {
    // nonce: '0x00', // ignored by MetaMask
    // gasPrice: '0x09184e72a000', // customizable by user during MetaMask confirmation.
    gas: '0x0', // customizable by user during MetaMask confirmation.
    to: '0x9d225E305758483AdD2A372B444acda6c0c21Fb1', // Required except during contract publications.
    from: ethereum.selectedAddress, // must match user's active address.
    value: '0x00', // Only required to send ether to the recipient from the initiating external account.
    data:
      '0x7f7465737432000000000000000000000000000000000000000000000000000000600057', // Optional, but used for defining smart contract creation and interaction.
    chainId: '0x5', // Used to prevent transaction reuse across blockchains. Auto-filled by MetaMask.
  };
  
  // txHash is a hex string
  // As with any RPC call, it may throw an error
  const txHash = await ethereum.request({
    method: 'eth_sendTransaction',
    params: [transactionParameters],
  });


}





function readContractFile(){

  // var contract_fp = "/Users/rahul/Documents/main/personal_learning_projects/creator_coin_new/creator_coin/nft_example_compiled_code.json";

  return new Promise( function(resolve, reject){

    // $.getJSON('./json_files/nft_example_compiled_code.json', function(data) {
    //   // console.log('json-data:', data)
    //   resolve(data);
    // });
 

  })

}


const testTwo = async (web3js, bytecode, abi) => {

  // const accounts = await web3js.eth.getAccounts();
  // console.log('account:', accounts)


  // const rawTx = {
  //   from: '0x9d225E305758483AdD2A372B444acda6c0c21Fb1',
  //   data: '0x' + bytecode
  // };

  let collectiblesFactory = new ethers.ContractFactory(
    abi,
    bytecode,
    ethersProvider.getSigner('0x607a24AaA95210FdDBa7b4837bFAb3B97f18bA7D')
  ); 

  collectiblesContract = await collectiblesFactory.deploy('testing-one', 'tt', 1000, 25, 100, 'https://docs.metamask.io/guide/sending-transactions.html');
  await collectiblesContract.deployTransaction.wait();

  console.log(
    `Contract mined! address: ${collectiblesContract.address} transactionHash: ${collectiblesContract.deployTransaction.hash}`,
  );
  // 0x91749c47c43e0141f369ce7ff315a951bb62b83a

  // // constructor(string memory tokenName, string memory tokenSymbol, uint256 totalSupply, uint256 maxNumPerSale, uint256 _userTokenPrice, string memory _userTokenURI) ERC721(tokenName, tokenSymbol) {
  // const deployedContract = await new web3js.eth.Contract(abi)
  // .deploy({
  //   data: '0x' + bytecode,
  //   arguments: ['testing-one', 'tt', 1000, 25, 100, 'https://docs.metamask.io/guide/sending-transactions.html']
  // })
  // .send({
  //   from: "0x9d225E305758483AdD2A372B444acda6c0c21Fb1",
  //   gas: '10000000'
  // });


  // console.log(deployedContract)

  // console.log(
  //   `Contract deployed at address: ${deployedContract.options.address}`
  // );

}


function getNFTData(){

  return new Promise(function(resolve, reject){
    
    // fetch metadata (ajax-request)
    fetch(API_HOST + "get-nft-metadata/")
    .then(response => response.json())
    .then(json => {
      // console.log('js:', json)
      resolve(json);
      
    })

  })

}


function saveNFTData() {

  return new Promise(function(resolve, reject){
    
    fetch(API_HOST + "save-nft-metadata/")
    .then(response => response.json())
    .then(json => {
      // console.log('js:', json)
      resolve(json);
    })

  })

}



function saveNFTLaunchedData(contractData, contractAddress){

  return new Promise(function(resolve, reject){

    $.ajax({
      type: 'POST',
      url: API_HOST + "nft-launch-final/",
      data: {
        csrfmiddlewaretoken: csrfToken,
        'nft_transaction_hash': contractData['hash'],
        'nft_deployed_data': contractData['data'],
        'nft_deployed_nonce': contractData['nonce'],
        'nft_deployed_chain_id': contractData['chainId'],
        'nft_contract_address': contractAddress
      },
      success: function (response) {
        console.log('res:', response);
        // TODO: refresh page?
  
        window.location.href = 'http://127.0.0.1:7500/profile/5/'

      }
  
    })

  })

}



const mainTestThree = async (bytecode, abi) => {

  // var mainProvider = await ethers.getDefaultProvider();
  // console.log(mainProvider)

  const provider = new ethers.providers.Web3Provider(window.ethereum);
  const network = await provider.getNetwork();
  const chainId = network.chainId;
  
  console.log('network:', network);
  console.log('chain-id:', chainId);

  const accounts = await provider.listAccounts();
  console.log('network-accounts:', accounts);
  
  console.log('eths-provider:', ethersProvider)

  let collectiblesFactory = new ethers.ContractFactory(
    abi,
    bytecode,
    ethersProvider.getSigner(accounts[0])
  ); 
  
  document.getElementById("overlay").style.display = "block";

  // document.getElementById("spinning_border").style.display = ''
  // document.getElementById("overlay").style.display = ''

  const nftSaveResp = await saveNFTData();

  document.getElementById("overlay").style.display = "none";;

  console.log('nft-save-resp:', nftSaveResp);

  if (nftSaveResp['success'] === true){  // deploy the token

    let nftMetaData = await getNFTData();

    // Load a metamask signature
    let collectiblesContract = await collectiblesFactory.deploy( 
      nftMetaData['nft_name'],
      nftMetaData['nft_symbol'],
      nftMetaData['nft_total_supply'],
      20, // max-token-sale-per-purchase
      Number(Web3.utils.toWei(nftMetaData['nft_price'], "ether")).toString(),
      nftMetaData['nft_ipfs_url']
    )

    // console.log('ts-new:', collectiblesContract.deployTransaction, collectiblesContract.address)
    // // 0x68Ea1a2504a4287900E51Db51658F21704F09720
    saveNFTLaunchedData(collectiblesContract.deployTransaction, collectiblesContract.address);

  // let transHash = await collectiblesContract.getDeployTransaction();
  // console.log('trans-hash:', transHash);
  // console.log('ts-new:', collectiblesContract.deployTransaction, collectiblesContract.address)

    // if user signs above, send request to verify the launched-nft
      // refresh page with views fetching associated etherscan data and buy-button being shown


  } else { // TODO: need to display error explaining what happened

  }  
 

  // TODO: AJAX request to upload the metadata to IPFS, save URL, send as response to here and go from there
 
  // TODO: below after the IPFS-URL is retrieved and saved in DB, under nft 
  // await collectiblesFactory.deploy(
  //   nftMetaData['nft_name'],
  //   nftMetaData['nft_symbol'],
  //   nftMetaData['nft_total_supply'],
  //   20, // max-token-sale-per-purchase
  //   Number(Web3.utils.toWei(nftMetaData['nft_price'], "ether")).toString(),

  // )

  // collectiblesContract = await collectiblesFactory.deploy('testing-one', 'tt', 500, 20, Number(Web3.utils.toWei("0.1", "ether")).toString(), 'https://docs.metamask.io/guide/sending-transactions.html');

    
  // collectiblesContract = await collectiblesFactory.deploy('testing-one', 'tt', 500, 20, Number(Web3.utils.toWei("0.1", "ether")).toString(), 'https://docs.metamask.io/guide/sending-transactions.html');
  // // let transHash = await collectiblesContract.getDeployTransaction();
  // // console.log('trans-hash:', transHash);
  // console.log('ts-new:', collectiblesContract.deployTransaction, collectiblesContract.address)

  // await collectiblesContract.deployTransaction.wait();
  
  // // console.log(
  // //   `Contract mined! address: ${collectiblesContract.address} transactionHash: ${collectiblesContract.deployTransaction.hash}`,
  // // );

}


const mainTestFour = async () => {
  const provider = new ethers.providers.Web3Provider(window.ethereum);
  const network = await provider.getNetwork();
  const chainId = network.chainId;

  const accounts = await provider.listAccounts();

  let esProvider = new ethers.providers.EtherscanProvider("goerli");
  let esHistory = await esProvider.getHistory(accounts[0]);
  console.log('es-hist:', esHistory)


}


// TODO: deploy on goerli testnet with signature and interact (purchase/fetch-data, etc.) with contract through webapp
// $( "#test-one-button" ).click(async () => {
$( "#launch-nft-button" ).click(async () => {
  
  fetch("http://127.0.0.1:7500/static/json_files/nft_main_compiled_code.json")
  .then(response => response.json())
  .then(json => {
    var bytecode = json["contracts"]["NFTMain.sol"]["CreatorNFT"]["evm"]["bytecode"]["object"];
    var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["CreatorNFT"]["metadata"] )["output"]["abi"];

    console.log('bytecode:', bytecode);
    console.log('abi:', abi);

    // // testTwo('', bytecode, abi);
    mainTestThree(bytecode, abi);
    // // mainTestFour()

  })
  
  // console.log('eth-selected-addr:', ethereum.selectedAddress);
  // // testOne()
  // // var web3js = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
  // var web3js = new Web3(new Web3.providers.HttpProvider("https://goerli.infura.io/v3/2101c205c1c447daa8ad7d7d9cb9bb5b"));
  // console.log('web3-js:', web3js)

  // // var contractData = await readContractFile();
  // // console.log('cd:', contractData);

  
  // fetch("http://127.0.0.1:7500/static/json_files/nft_example_compiled_code.json")
  // .then(response => response.json())
  // .then(json => {
  //   var bytecode = json["contracts"]["NFTExample.sol"]["NFTExample"]["evm"]["bytecode"]["object"];
  //   var abi = JSON.parse( json["contracts"]["NFTExample.sol"]["NFTExample"]["metadata"] )["output"]["abi"];

  //   console.log('bytecode:', bytecode);
  //   console.log('abi:', abi);

  //   testTwo(web3js, bytecode, abi);

  }
    
);

  // # get bytecode
  // bytecode = compiled_sol["contracts"]["NFTExample.sol"]["NFTExample"]["evm"]["bytecode"]["object"]
  // # get abi
  // abi = json.loads(compiled_sol["contracts"]["NFTExample.sol"]["NFTExample"]["metadata"])["output"]["abi"]

  // $.getJSON(contract_fp, function(data) {
  //   // console.log('json-data:', data)
  //   resolve(data);
  // });

  // const deployedContract = await new web3.eth.Contract(compiledContract.abi)

  
  // await currentProvider.request({ method: 'eth_requestAccounts' });
  // let web3 = new Web3(currentProvider);

// })



const rndOne = async (abi, bytecode) => {

  var contractAddr = '0xE8eFDd47f950FA19E361A51B820a61D99049f921';

  var existingContract = new ethers.Contract(
    contractAddr,
    abi,
    ethersProvider.getSigner('0x9B647554B338d02ee67f4F6C0f335750f77924DA')
  );

  // 0x607a24AaA95210FdDBa7b4837bFAb3B97f18bA7D
  // 0x607a24AaA95210FdDBa7b4837bFAb3B97f18bA7D

  console.log(existingContract)
  var tokPrice = await existingContract.getTokenPrice();
  console.log('tok-price:', tokPrice);
  var tokMaxSupply = await existingContract.getMaxTokenSupply();
  console.log('tok-supply:', tokMaxSupply);
  var currentTokenID = await existingContract.getCurrentTokenID();
  console.log('tok-ID:', currentTokenID);
 
  // // TODO: deploy to IPFS
  // var currentTokenURI = await existingContract.tokenURI(0);
  // console.log('tok-uri:', currentTokenURI);

  // var tokenOwner = await existingContract.ownerOf(0);
  // console.log('tok-owner:', tokenOwner);

  // when user buys
  var numTokens = 1;
  let result = await existingContract.safeMint(numTokens, {'value': 100});
  // result = await existingContract.wait();
  console.log('result:', result)  // get transaction-hash/link from block-explorer and put on page


}



$( "#test-two-button" ).click(function() {


  fetch("http://127.0.0.1:7500/static/json_files/nft_main_compiled_code.json")
  .then(response => response.json())
  .then(json => {
    var bytecode = json["contracts"]["NFTMain.sol"]["CreatorNFT"]["evm"]["bytecode"]["object"];
    var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["CreatorNFT"]["metadata"] )["output"]["abi"];

    // console.log('bytecode:', bytecode);
    // console.log('abi:', abi);

    rndOne(abi, bytecode);


  })


})


function get_nft_bytecode_abi(){

  return new Promise(function(resolve, reject){

    fetch("http://127.0.0.1:7500/static/json_files/nft_main_compiled_code.json")
    .then(response => response.json())
    .then(json => {
      var bytecode = json["contracts"]["NFTMain.sol"]["CreatorNFT"]["evm"]["bytecode"]["object"];
      var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["CreatorNFT"]["metadata"] )["output"]["abi"];

      resolve({'bytecode': bytecode, 'abi': abi});

    })  


  })

}



function get_nft_contract_address(creatorProfileID){

  return new Promise(function(resolve, reject){
    
    // fetch metadata (ajax-request)
    
    fetch(API_HOST + "fetch-nft-main-data/" + creatorProfileID)
    .then(response => response.json())
    .then(json => {

      // if (json['redirect'] === true){
      //   window.location.href = 'http://127.0.0.1:7500/logout'
      // }
      resolve(json);

    })

  })

}


const buyNFTMain = async () => {
  
  var bytecodeDict = await get_nft_bytecode_abi();
  var contractABI = bytecodeDict['abi']
  // var contractByteCode = bytecodeDict['bytecode']
  
  // console.log('href:', window.location.href )
  // var profileUrl = window.location.href
  // var profileID = profileUrl.split("/")
  // console.log(profileID)

  var contractData = await get_nft_contract_address(creatorProfileID);
  // console.log('ct-data:', contractData);
  var mainContractAddress = contractData['nft_contract_address'];
  console.log('main-contract-addr:', mainContractAddress)
  
  var existingContract = new ethers.Contract(
    mainContractAddress,
    contractABI,
    ethersProvider.getSigner()
  ); 
 
  console.log('existing-contract:', existingContract);
  
  var tokPrice = await existingContract.getTokenPrice();
  console.log('tok-price:', tokPrice);
  console.log('tok-number:', ethers.utils.formatEther( tokPrice ) )
    
  var numTokens = 1;
  let result = await existingContract.safeMint(numTokens, {'value': "1200000000000000000"});
  // result = await existingContract.wait();
  console.log('result:', result)  // get transaction-hash/link from block-explorer and put on page

  // TODO: 
    // buy --> balance needs to be deducted from current user and platform-address needs to receive money
      // ensure this is correct and go from there

 
  // var tokMaxSupply = await existingContract.getMaxTokenSupply();
  // console.log('tok-supply:', tokMaxSupply);
  
  
  // fetch("http://127.0.0.1:7500/static/json_files/nft_main_compiled_code.json")
  // .then(response => response.json())
  // .then(json => {
  //   var bytecode = json["contracts"]["NFTMain.sol"]["CreatorNFT"]["evm"]["bytecode"]["object"];
  //   var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["CreatorNFT"]["metadata"] )["output"]["abi"];

  //   // console.log('bytecode:', bytecode);
  //   // console.log('abi:', abi);

  //   // // // testTwo('', bytecode, abi);
  //   // mainTestThree(bytecode, abi);
  //   // // // mainTestFour()

  //   // var contractData = await get_nft_contract_address();
    
  //   nft_deployed_contract_address
  //   var contractAddr = '0xE8eFDd47f950FA19E361A51B820a61D99049f921';

  //   var existingContract = new ethers.Contract(
  //     contractAddr,
  //     abi,
  //     ethersProvider.getSigner('0x9B647554B338d02ee67f4F6C0f335750f77924DA')
      
  //   );

  // })


}


$( "#buy-nft" ).click(function() {

  buyNFTMain();

  // // fetch("http://127.0.0.1:7500/static/json_files/nft_main_compiled_code.json")
  // fetch(API_HOST + "fetch-nft-main-data/")
  // .then(response => response.json())
  // .then(json => {
  //   var bytecode = json["contracts"]["NFTMain.sol"]["CreatorNFT"]["evm"]["bytecode"]["object"];
  //   var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["CreatorNFT"]["metadata"] )["output"]["abi"];

  //   // console.log('bytecode:', bytecode);
  //   // console.log('abi:', abi);

  //   // // // testTwo('', bytecode, abi);
  //   // mainTestThree(bytecode, abi);
  //   // // // mainTestFour()

  //   var contractData = await get_nft_contract_address();
    
  //   nft_deployed_contract_address
  //   var contractAddr = '0xE8eFDd47f950FA19E361A51B820a61D99049f921';

  //   var existingContract = new ethers.Contract(
  //     contractAddr,
  //     abi,
  //     ethersProvider.getSigner('0x9B647554B338d02ee67f4F6C0f335750f77924DA')
      
  //   );


  // })


})





