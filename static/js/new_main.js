const API_HOST = 'http://127.0.0.1:7500/'

let ethersProvider;
let loginErrorModal;
let loginErrorTwoModal;
let loginErrorThreeModel;


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


const handleSignupButtonClick = async () => {

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
              window.location.href = 'http://127.0.0.1:7500/profile/' + userLoginInfoRes['profile_id'];  // TODO: redirect to profile?
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










// Eth Listeners
if (window.ethereum){

  window.ethereum.on('accountsChanged', (accounts) => {

    console.log('account-changed:', accounts);
    // handleAccountChange();
    window.location.href = 'http://127.0.0.1:7500/logout';
  
  });
  
}

if (window.ethereum){

  window.ethereum.on('chainChanged', (chainId) => {

    console.log('chain-changed:', chainId);
    // window.location.reload();
    window.location.href = 'http://127.0.0.1:7500/logout';

  })

};


// User switch works 
  // **user connnected does not work <-- need to ensure user is connected 

 





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




// TODO: 
  // verify github seemed to verify my GH in new tab and logged me out? 
    // verify on same tab and just reload page with new data on page
  // try it in chrome incog and go from there





