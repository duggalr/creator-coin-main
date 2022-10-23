const API_HOST = 'http://127.0.0.1:7500/'

let ethersProvider;
let loginErrorModal;
let loginErrorTwoModal;
let loginErrorThreeModel;
let projectLogModal;



var loginModalExists = document.getElementById("loginErrorOne");
if (loginModalExists != null){  // on homepage
  loginErrorModal = new bootstrap.Modal('#loginErrorOne');
  loginErrorTwoModal = new bootstrap.Modal('#loginErrorTwo');
  loginErrorThreeModel = new bootstrap.Modal('#loginErrorThree');
}


let nftVerificationModal;

var nftVerificationModalExists = document.getElementById('nftVerificationModal');
if (nftVerificationModalExists != null){
  nftVerificationModal = new bootstrap.Modal('#nftVerificationModal')
}


var projectLogModalExists = document.getElementById("projectLogModal");
if (projectLogModalExists != null){
  projectLogModal = new bootstrap.Modal('#projectLogModal');
}



function requestNonce(user_account_pk_address){

  return new Promise(function(resolve, reject){

    var apiURL = new URL(API_HOST + 'generate_nonce?');
    apiURL.searchParams.append('web3_address', user_account_pk_address);
    // const user_nonce_res = await axios.get(apiURL.href)
  
    fetch(apiURL)
    .then(response => response.json())
    .then(json => {

      resolve(json)
  
    })
    
  })

}


function completeLogin(userData){

  return new Promise(function(resolve, reject){

    var apiURL = new URL(API_HOST + "login/");
    fetch(apiURL, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    }).then(response => response.json()).then(json => {

      resolve(json);

    })
    
  })

}


const handleSignupButtonClick = async (redirect_profile_id) => {

  if (window.ethereum && window.ethereum.isMetaMask) {

    const walletUnlocked =  await window.ethereum._metamask.isUnlocked();  // need to access 'experimental'-api
    if (walletUnlocked === true){

      // TODO: specifying 'any' due to any blockchain allowed; change to only main-net? 
      ethersProvider = new ethers.providers.Web3Provider(window.ethereum, 'any');

      // MetaMask requires requesting permission to connect users accounts
      await ethersProvider.send("eth_requestAccounts", []);

      const signer = ethersProvider.getSigner();
      // console.log('signer:', signer)
      
      const userAccounts = await ethersProvider.listAccounts();
      // console.log('user-accounts:', userAccounts);

      const user_account_pk_address = userAccounts[0];

      // const userNonceJson = await getNonce(user_account_pk_address);
      // console.log('user-nonce:', userNonceJson);

      let userNonceRes;
      try{
        userNonceRes = await requestNonce(user_account_pk_address);
        // console.log('user-nonce-res:', userNonceRes)
      } catch(error){  // user-nonce-request with response != 200 (rare situation)
        loginErrorThreeModel.show();
      }

      if (userNonceRes['success'] === true){

        let userNonce = userNonceRes['data']['nonce'];

        var message = "\nBy signing this message, you will sign the randomly generated nonce.  \n\nNonce: " + userNonce + " \n\nWallet Address: " + user_account_pk_address
        
        let userSignature;
        try{
          userSignature = await signer.signMessage(message);
        } catch(error) {
          console.log(error);
        }

        if (userSignature){

          const data = {
            pk_address: user_account_pk_address,
            nonce_signature: userSignature,
          };

          try{
            let userLoginInfoRes = await completeLogin(data);
            if (userLoginInfoRes['success'] === true){
              if (redirect_profile_id !== undefined) {
                window.location.href = 'http://127.0.0.1:7500/profile/' + redirect_profile_id + '?click=buy-button'
                // buyNFTMain()
              } else {
                window.location.href = 'http://127.0.0.1:7500/profile/' + userLoginInfoRes['profile_id'];
              }

              
            }
          } catch(error) {  // user login request failed
            console.log(error)
          }
          

        } else { // signature denied.

          // alert("MetaMask Signature Denied.")

        }

      }


    } else { // wallet is not unlocked

      loginErrorTwoModal.show();
      
    }


  } else {

    loginErrorModal.show();

  }


}


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
  
        window.location.href = 'http://127.0.0.1:7500/profile/' + creatorProfileID

      }
  
    })

  })

}



const mainTestThree = async (bytecode, abi) => {

  const provider = new ethers.providers.Web3Provider(window.ethereum);
  const network = await provider.getNetwork();
  const chainId = network.chainId;
  
  console.log('network:', network);
  console.log('chain-id:', chainId);

  const accounts = await provider.listAccounts();
  console.log('network-accounts:', accounts);

  // console.log('ets-provider:', ethersProvider)

  let collectiblesFactory = new ethers.ContractFactory(
    abi,
    bytecode,
    provider.getSigner(accounts[0])
  ); 
  
  document.getElementById("overlay").style.display = "block";


  let nftSaveResp;
  try {
    nftSaveResp = await saveNFTData();
    // userNonceRes = await requestNonce(user_account_pk_address);
    // console.log('user-nonce-res:', userNonceRes)
  } catch(error){  // user-nonce-request with response != 200 (rare situation)
    // loginErrorThreeModel.show();
    console.log('error:', error)
  }

  // const nftSaveResp = await saveNFTData();

  document.getElementById("overlay").style.display = "none";;

  console.log('nft-save-resp:', nftSaveResp);

  if (nftSaveResp['success'] === true){  // deploy the token

    let nftMetaData;
    try {
      nftMetaData = await getNFTData();
    } catch(error){
      console.log('error:', error)
    }

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





function get_nft_contract_address(creatorProfileID){

  return new Promise(function(resolve, reject){
    
    // fetch metadata (ajax-request)
    
    fetch(API_HOST + "fetch-nft-main-data/" + creatorProfileID)
    .then(response => response.json())
    .then(json => {

      resolve(json);

    })

  })

}



function saveTransactionData(result){

  // console.log('creator-profile-id:', creatorProfileID)

  return new Promise(function(resolve, reject){

    $.ajax({
      type: 'POST',
      url: API_HOST + "save-nft-transaction-data/",
      data: {
        csrfmiddlewaretoken: csrfToken,
        'profile_id': creatorProfileID,
        'nft_transaction_hash': result['hash']
      },
      success: function (response) {
        console.log('res:', response);
        // TODO: refresh page?
        // window.location.href = 'http://127.0.0.1:7500/profile/' + creatorProfileID
        if (response['success'] === true){
          window.location.href = 'http://127.0.0.1:7500/profile/' + response['redirect_profile_id']
        } else { // TODO: display error message in modal
          console.log('you must be logged in...')
        }

      }
  
    })

  })

}



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





const buyNFTMain = async () => {

  // Determine if user is logged in or not

  console.log('anon-user:', anonUser)

  if (anonUser === 'True'){
    
    handleSignupButtonClick(creatorProfileID)

  } else {

    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const network = await provider.getNetwork();
    const chainId = network.chainId;
    
    // console.log('network:', network);
    // console.log('chain-id:', chainId);
  
    const accounts = await provider.listAccounts();
    // console.log('network-accounts:', accounts);
  
  
    let bytecodeDict;
    try{
      bytecodeDict = await get_nft_bytecode_abi();
    } catch(error){
      console.log(error)
    }
    
    if (typeof bytecodeDict !== undefined){
  
      var contractABI = bytecodeDict['abi']
  
      let contractData;
      try{
        contractData = await get_nft_contract_address(creatorProfileID);
      } catch(error) {
        console.log(error)
      }
  
      if (typeof contractData !== undefined){
  
        // console.log('ct-data:', contractData);
        var mainContractAddress = contractData['nft_contract_address'];
        var tokenPrice = contractData['nft_token_price'];
        // var tokenSupply = contractData['nft_token_supply'];
  
        console.log('main-contract-addr:', mainContractAddress)
  
        var existingContract = new ethers.Contract(
          mainContractAddress,
          contractABI,
          provider.getSigner(accounts[0])
        ); 
  
        // console.log('existing-contract:', existingContract);
  
        // console.log('ct-data:', contractData)
        // var tokPriceStr = (tokenPrice * (10**18)).toString();
        // console.log('tok-price-str:', tokPriceStr, tokenPrice);
        
        // var numTokens = 1;
        var tokPriceStr = (tokenPrice * (10**18)).toString();
        try {
          let result = await existingContract.safeMint(1, {'value': tokPriceStr});
          // // result = await existingContract.wait();
          console.log('result:', result)  // get transaction-hash/link from block-explorer and put on page
          
          saveTransactionData(result)
  
        } catch(error){
  
        }
        
  
      }
      
    }

  }



  
  // var tokPrice = await existingContract.getTokenPrice();
  // console.log('tok-price:', tokPrice);
  // console.log('tok-number:', ethers.utils.formatEther( tokPrice ) )
    
  // // var numTokens = 1;
  // var tokPriceStr = (tokPrice * (10**18)).toString();
  // let result = await existingContract.safeMint(numTokens, {'value': tokPriceStr});
  // // result = await existingContract.wait();
  // console.log('result:', result)  // get transaction-hash/link from block-explorer and put on page


}






// Eth Listeners
if (window.ethereum){

  window.ethereum.on('accountsChanged', (accounts) => {

    console.log('account-changed:', accounts);
    handleAccountChange();
    // window.location.href = 'http://127.0.0.1:7500/logout';
  
  });
  
}


if (window.ethereum){

  window.ethereum.on('chainChanged', (chainId) => {

    console.log('chain-changed:', chainId);
    window.location.reload();
    // window.location.href = 'http://127.0.0.1:7500/logout';

  })

};


 



// DOM Listeners

var signupLinkClicked;
$('#main-signup-login-button').on('click', function(){

  if (signupLinkClicked){ // prevent multiple clicks
    return false;
  } else {
    signupLinkClicked = true;
    handleSignupButtonClick();
  }

})



function verifyProfileDetails(){

  return new Promise(function(resolve, reject){

    var apiURL = new URL(API_HOST + 'verify_user_profile');
    // console.log('api-url:', apiURL)

    // Verify profile details
    $.ajax({
      url: apiURL,
      success: function (response) {
        console.log('res:', response);
        
        if (response['success'] === false){

          // console.log('nft-verf-modal:', nftVerificationModal);
          nftVerificationModal.show();

        } else if (response['success'] === true){

          window.location.href = 'http://127.0.0.1:7500/create-nft'

        }

      }

    })


  })

}



const handleCreateNFTClick = async () => {

  await verifyProfileDetails();

}


var userCreateNFTClicked;
$( "#user_create_nft" ).click(function() {
      
  if (userCreateNFTClicked){
    return false;
  } else {
    userCreateNFTClicked = true;
    handleCreateNFTClick();
  }

});



var launchNFTClicked;
$( "#launch-nft-button" ).click(async () => {

  if (launchNFTClicked){
    return false;
  } else {
    launchNFTClicked = true;

    fetch("http://127.0.0.1:7500/static/json_files/nft_main_compiled_code.json")
    .then(response => response.json())
    .then(json => {
      var bytecode = json["contracts"]["NFTMain.sol"]["CreatorNFT"]["evm"]["bytecode"]["object"];
      var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["CreatorNFT"]["metadata"] )["output"]["abi"];
  
      console.log('bytecode:', bytecode);
      console.log('abi:', abi);
  
      mainTestThree(bytecode, abi);
  
    })

  }

  

  
});




var userBuyNFTClicked;
$( "#buy-nft-buttton" ).click(async () => {

  if (userBuyNFTClicked){
    return false;
  } else {
    userBuyNFTClicked = true;
    // TODO:
    buyNFTMain()
  }


})



$( "#delete-nft-button" ).click(async () => {

  alert("Implement Delete Button")

})



$( "#post-update-button" ).click(async () => {

  projectLogModal.show();

})


// $("#project-log-update-button").click(async () => {

// })

  

// // Homepage DOM
// TODO: finish this and go from there
$('#join_beta_form').submit(function(e){

  e.preventDefault();

  var user_email = $('#user_email_value').val();
  $.ajax({
    type: 'POST',
    url: "",
    data: {
      'user_email': user_email,
      csrfmiddlewaretoken: homepageCSRFTok
    },
    success: function (response) {
      console.log('res:', response);
      
      if (response['success'] === true){

        // success_message
        
        $('#join_beta_form').hide();
        $('#success_message').show();

      } else if (response['duplicate'] === true){

        $('#join_beta_form').hide();
        $('#duplicate_message').show();

      }

    }

  })

})





