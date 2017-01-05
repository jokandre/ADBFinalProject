// This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {
  console.log(response);
  // The response object is returned with a status field that lets the
  // app know the current login status of the person.
  // Full docs on the response object can be found in the documentation
  // for FB.getLoginStatus().
  if (response.status === 'connected') {
    // Logged into your app and Facebook.
    console.log(response.authResponse.accessToken);
     token = response.authResponse.accessToken;
    FB.api('/me', {fields: 'name,gender,email,friends,likes,picture'}, function(response) {
      //user的資料在這裡
      console.log(response);
      get_user(response, token)
      // ajax and redirect to index.html
    });
  } else if (response.status === 'not_authorized') {
    // The person is logged into Facebook, but not your app.
    document.getElementById('status').innerHTML = 'Please log ' +
      'into this app.';
  } else {
    // The person is not logged into Facebook, so we're not sure if
    // they are logged into this app or not.
    document.getElementById('status').innerHTML = 'Please log ' +
      'into Facebook.';
  }
}

// This function is called when someone finishes with the Login
// Button.  See the onlogin handler attached to it in the sample
// code below.
function checkLoginState() {
  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });
}

window.fbAsyncInit = function() {
FB.init({
  appId      : '247334179013123',
  cookie     : true,  // enable cookies to allow the server to access
                      // the session
  xfbml      : true,  // parse social plugins on this page
  version    : 'v2.8' // use graph api version 2.8
});

// Now that we've initialized the JavaScript SDK, we call
// FB.getLoginStatus().  This function gets the state of the
// person visiting this page and can return one of three states to
// the callback you provide.  They can be:
//
// 1. Logged into your app ('connected')
// 2. Logged into Facebook, but not your app ('not_authorized')
// 3. Not logged into Facebook and can't tell if they are logged into
//    your app or not.
//
// These three cases are handled in the callback function.

FB.getLoginStatus(function(response) {
  statusChangeCallback(response);
});

};

// Load the SDK asynchronously
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

// Here we run a very simple test of the Graph API after login is
// successful.  See statusChangeCallback() for when this call is made.

function fb_login(){
  // FB 第三方登入
  FB.login(function(response)
  {
      //statusChangeCallback(response);
      if (response.authResponse) {
        console.log('Welcome!  Fetching your information.... ');
        location.reload();
      } else {
        console.log('User cancelled login or did not fully authorize.');
      }
  }, {scope: 'public_profile,email,user_friends,user_likes'});
}

function get_user(fb,token) {
    FB.api('/me', function(response) {
    $.ajax({
      url: '/login',
      data:JSON.stringify({
        id:fb.id,
        name:fb.name,
        email: fb.email,
        gender: fb.gender,
        access_token:token,
        portrait: fb.picture.data.url
      }),
      type:'POST',
      contentType:"application/json",
      datatype:'application/json',
      success:function(response){
        console.log("Just registered!")
        window.location = "http://140.114.77.15:5000/index";
      },
      error:function(error){
        console.log(error);
      }
    });
  });
}
