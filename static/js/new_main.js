const API_HOST = location.protocol + '//' + location.host + '/';

let ethersProvider;
let loginErrorModal;
let loginErrorTwoModal;
let loginErrorThreeModel;
let loginErrorFourModel;

let projectLogModal;
let nftVerificationModal;
let chainIdErrorModal;
let numTokensErrorModal;

let createUserNFTBetaModal;


var loginModalExists = document.getElementById("loginErrorFour");
if (loginModalExists != null){  // on homepage
  loginErrorModal = new bootstrap.Modal('#loginErrorOne');
  loginErrorTwoModal = new bootstrap.Modal('#loginErrorTwo');
  loginErrorThreeModel = new bootstrap.Modal('#loginErrorThree');
  loginErrorFourModel = new bootstrap.Modal('#loginErrorFour');
}


var loginModalExists = document.getElementById("loginErrorOne");
if (loginModalExists != null){  // on homepage
  loginErrorModal = new bootstrap.Modal('#loginErrorOne');
  loginErrorTwoModal = new bootstrap.Modal('#loginErrorTwo');
  loginErrorThreeModel = new bootstrap.Modal('#loginErrorThree');
}


var nftVerificationModalExists = document.getElementById('nftVerificationModal');
if (nftVerificationModalExists != null){
  nftVerificationModal = new bootstrap.Modal('#nftVerificationModal')
}


var projectLogModalExists = document.getElementById("projectLogModal");
if (projectLogModalExists != null){
  projectLogModal = new bootstrap.Modal('#projectLogModal');
}


var chainIdModalExists = document.getElementById("chainIDErrorModal");
if (chainIdModalExists != null){
  chainIdErrorModal = new bootstrap.Modal('#chainIDErrorModal');
}


var numTokensModalExists = document.getElementById("numTokensErrorModal");
if (numTokensModalExists != null){
  numTokensErrorModal = new bootstrap.Modal('#numTokensErrorModal');
}


var userNFTModalExists =  document.getElementById("user_beta_email_modal");
if (userNFTModalExists != null){
  createUserNFTBetaModal = new bootstrap.Modal('#user_beta_email_modal');
}



function requestNonce(user_account_pk_address){

  return new Promise(function(resolve, reject){

    var apiURL = new URL(API_HOST + 'generate_nonce?');
    apiURL.searchParams.append('web3_address', user_account_pk_address);
    
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

    if (walletUnlocked === true) {

      ethersProvider = new ethers.providers.Web3Provider(window.ethereum, 'any');

      const provider = new ethers.providers.Web3Provider(window.ethereum);
      const network = await provider.getNetwork();
      const chainId = network.chainId;

      if (chainId === 1){ // ethereum mainnet

        // MetaMask requires requesting permission to connect users accounts
        await ethersProvider.send("eth_requestAccounts", []);
  
        const signer = ethersProvider.getSigner();
        
        const userAccounts = await ethersProvider.listAccounts();

        const user_account_pk_address = userAccounts[0];

        let userNonceRes;
        try {
          userNonceRes = await requestNonce(user_account_pk_address);
        } catch(error) {  // user-nonce-request with response != 200 (rare situation)
          loginErrorThreeModel.show();
          signupLinkClicked = false;
        }


        if (userNonceRes['success'] === true){

          let userNonce = userNonceRes['data']['nonce'];

          var message = "\nBy signing this message, you will sign the randomly generated nonce.  \n\nNonce: " + userNonce + " \n\nWallet Address: " + user_account_pk_address
          
          let userSignature;
          try {
            userSignature = await signer.signMessage(message);
          } catch(error) {
            console.log(error);
            signupLinkClicked = false;
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
                  window.location.href = API_HOST + 'profile/' + redirect_profile_id + '?click=buy-button';
                  
                } else {
                  window.location.href = API_HOST + 'profile/' + userLoginInfoRes['profile_id'];
                }

              } else {
                loginErrorThreeModel.show();
                signupLinkClicked = false;
              }

            } catch(error) {  // user login request failed
              loginErrorThreeModel.show();
              signupLinkClicked = false;
            }

          } else { // signature denied.

            signupLinkClicked = false;

          }

        } else {

          loginErrorThreeModel.show();
          signupLinkClicked = false;
          
        }


      } else {

        loginErrorFourModel.show();
        signupLinkClicked = false;

      }


    } else { // wallet is not unlocked

      loginErrorTwoModal.show();
      signupLinkClicked = false;

    }


  } else {

    loginErrorModal.show();
    signupLinkClicked = false;

  }


}


function handleAccountChange(){

  return new Promise(function(){
    
    // fetch metadata (ajax-request)
    fetch(API_HOST + "handle-account-change/")
    .then(response => response.json())
    .then(json => {

      if (json['redirect'] === true){
        window.location.href = API_HOST + 'logout';
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
      resolve(json);
    })

  })

}


function saveNFTData() {

  return new Promise(function(resolve, reject){
    
    fetch(API_HOST + "save-nft-metadata/")
    .then(response => response.json())
    .then(json => {
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
        
        if (response['success'] === true){
          window.location.href = API_HOST + 'profile/' + creatorProfileID;
        }

      }
  
    })

  })

}




const mainTestThree = async (bytecode, abi) => {

  const provider = new ethers.providers.Web3Provider(window.ethereum);
  const network = await provider.getNetwork();
  const chainId = network.chainId;
  
  if (chainId != 1){  // Chain-ID check; display error modal

    launchNFTClicked = false;
    chainIdErrorModal.show();

  } else {

    const accounts = await provider.listAccounts();
  
    let collectiblesFactory = new ethers.ContractFactory(
      abi,
      bytecode,
      provider.getSigner(accounts[0])
    ); 
    
    document.getElementById("overlay").style.display = "block";
  
  
    let nftSaveResp;
    try {
      nftSaveResp = await saveNFTData();
    } catch(error){  // user-nonce-request with response != 200 (rare situation)
      launchNFTClicked = false;
    }
  
    document.getElementById("overlay").style.display = "none";;
  
    if (nftSaveResp['success'] === true){  // deploy the token
  
      let nftMetaData;
      try {
        nftMetaData = await getNFTData();
      } catch(error){
        console.log('error:', error);
        launchNFTClicked = false;
      }
  
      try {

        // Load a metamask signature
        let collectiblesContract = await collectiblesFactory.deploy( 
          nftMetaData['nft_name'],
          nftMetaData['nft_symbol'],
          nftMetaData['nft_total_supply'],
          20, // max-token-sale-per-purchase
          Number(Web3.utils.toWei(nftMetaData['nft_price'], "ether")).toString(),
          nftMetaData['nft_ipfs_url']
        )

        saveNFTLaunchedData(collectiblesContract.deployTransaction, collectiblesContract.address);

      } catch(error) {
        launchNFTClicked = false;
      }

    } else { // TODO: need to display error explaining what happened
  
      launchNFTClicked = false;

    }

  }

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



function saveTransactionData(result, tokensBought){

  return new Promise(function(resolve, reject){

    $.ajax({
      type: 'POST',
      url: API_HOST + "save-nft-transaction-data/",
      data: {
        csrfmiddlewaretoken: csrfToken,
        'profile_id': creatorProfileID,
        'nft_transaction_hash': result['hash'],
        'number_of_tokens_bought': tokensBought,
      },
      success: function (response) {

        if (response['success'] === true){
          window.location.href = API_HOST + 'profile/' + response['redirect_profile_id'];

        } else { // TODO: display error message in modal
          // console.log('you must be logged in...')
        }

      }
  
    })

  })

}



function get_nft_bytecode_abi(){

  return new Promise(function(resolve, reject){

    fetch("https://creator-coin-main.s3.ca-central-1.amazonaws.com/static/json_files/nft_main_new_compiled_code.json")
    .then(response => response.json())
    .then(json => {
      var bytecode = json["contracts"]["NFTMain.sol"]["NFTMain"]["evm"]["bytecode"]["object"];
      var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["NFTMain"]["metadata"] )["output"]["abi"];
      
      resolve({'bytecode': bytecode, 'abi': abi});

    })  


  })

}





const buyNFTMain = async () => {

  if (anonUser === 'True'){ // Determine if user is logged in or not
    
    handleSignupButtonClick(creatorProfileID)

  } else {

    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const network = await provider.getNetwork();
    const chainId = network.chainId;

    if (chainId != 1){  // display error modal

      chainIdErrorModal.show();

    } else {

      const accounts = await provider.listAccounts();
    
      let bytecodeDict;
      try{
        bytecodeDict = await get_nft_bytecode_abi();
      } catch(error){
        // console.log(error)
      }
      
      if (typeof bytecodeDict !== undefined){
    
        var contractABI = bytecodeDict['abi']
    
        let contractData;
        try{
          contractData = await get_nft_contract_address(creatorProfileID);
        } catch(error) {
          // console.log(error)
        }
    
        if (typeof contractData !== undefined){
    
          var mainContractAddress = contractData['nft_contract_address'];
          var tokenPrice = contractData['nft_token_price'];
          
          var existingContract = new ethers.Contract(
            mainContractAddress,
            contractABI,
            provider.getSigner(accounts[0])
          ); 
    

          var numTokens = parseInt( $('#num_token_to_buy').val() )
          if (numTokens > 0 && numTokens <= 20){

            var totalEthAmount = numTokens * tokenPrice;
            var tokPriceStr = "0x" + Web3.utils.toBN(Web3.utils.toWei(String(totalEthAmount), "ether")).toString(16)
            
            try {
  
              let result = await existingContract.safeMint(numTokens, {'value': tokPriceStr});             
              saveTransactionData(result, numTokens);
      
            } catch(error){
      
              userBuyNFTClicked = false;

            }

          } else {

            numTokensErrorModal.show();
            userBuyNFTClicked = false;

          }
          
    
        }
        
      }

    }


  }

}




// Eth Listeners
if (window.ethereum){ // Account Change

  window.ethereum.on('accountsChanged', (accounts) => {

    handleAccountChange();
  
  });
  
}

const targetChainID = '0x1'; // goerli testnet

if (window.ethereum){ // Chain Change

  window.ethereum.on('chainChanged', (chainId) => {

    if (chainId != targetChainID){
      window.location.reload();
    }

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

    // Verify profile details
    $.ajax({
      url: apiURL,
      success: function (response) {
        
        if (response['success'] === false){

          nftVerificationModal.show();

        } else if (response['success'] === true){

          window.location.href = API_HOST + 'create-nft/';

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
    handleCreateNFTClick();
  }

});


var launchNFTClicked;
$( "#launch-nft-button" ).click(async () => {

  if (launchNFTClicked){
    return false;

  } else {

    launchNFTClicked = true; 

    fetch("https://creator-coin-main.s3.ca-central-1.amazonaws.com/static/json_files/nft_main_new_compiled_code.json")
    .then(response => response.json())
    .then(json => {
      var bytecode = json["contracts"]["NFTMain.sol"]["NFTMain"]["evm"]["bytecode"]["object"];
      var abi = JSON.parse( json["contracts"]["NFTMain.sol"]["NFTMain"]["metadata"] )["output"]["abi"];

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
    buyNFTMain()

  }
})


$( "#delete-nft-button" ).click(async () => {
  alert("Implement Delete Button")
})


$( "#post-update-button" ).click(async () => {
  projectLogModal.show();
})


// // Homepage DOM

// Homepage Join Email Beta Form
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



$('#num_token_to_buy').on('input',function(e){
   
  var numTokenToBuy = $('#num_token_to_buy').val();

  $('#buy_total_cost').text( ' ' + (numTokenToBuy * nftMainPrice).toFixed(2) ) ;

});


$('#create_user_nft_beta').on('click', function(){
  
  createUserNFTBetaModal.show();

})







