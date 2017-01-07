function getusergeo() {
    var inilat = 25.037;
    var inilng = 121.56693799999994;
    var option = {
        enableHighAccuracy: true,
        maximumAge: 600000,
        timeout: 5000
    }
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError, option);
    } else {
        //alert("Geolocation is not supported by this browser.");
        showmap(inilat, inilng);
    }
}

function getusergeoagain(firerr) {
    if (error.code == error.TIMEOUT) {
        var option = {
            enableHighAccuracy: false,
            maximumAge: 600000,
            timeout: 10000
        }
        navigator.geolocation.getCurrentPosition(showPosition, showError, option);
    }
    else{
        showError(firerr);
    }
}

function showPosition(data) {
    var inilat = data.coords.latitude + 0;
    var inilng = data.coords.longitude + 0;

    $.ajax({
        url: 'http://140.114.77.15:5000/member/api/v1/me/update-location',
        data:JSON.stringify({
            latitude: inilat,
            longitude: inilng
        }),
        type:'POST',
        contentType:"application/json",
        datatype:'application/json',
        success:function(response){
            alert('ok');
            getNearbyPeople();
            showmap(inilat, inilng);
        },
        error:function(error){
            console.log(error);
        }
    });
}

function showError(error) {
    var inilat = 25.037;
    var inilng = 121.56693799999994;
    switch (error.code) {
        case error.PERMISSION_DENIED:
            //alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            //alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            //alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            //alert("An unknown error occurred.");
            break;
    }
    //showmap(inilat, inilng);
}

function showmap(inilat, inilng) {
    //map starts

    //db initial
    // var db = openDatabase('maplocate', '1.0', 'maps DB', 2 * 1024 * 1024);
    // db.transaction(function(tx) {
    //     tx.executeSql('CREATE TABLE IF NOT EXISTS locate (id,lat, lng)');
    // });
    // var f = 0;
    //db end
    var map = new google.maps.Map(document.getElementById('map'), {
        center: new google.maps.LatLng(inilat, inilng),
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    //map ends

    if (inilat != 25.037) {
        //user geostart
        var usericon = '../static/images/mapmarker/locate.png';
        var userll = new google.maps.LatLng(inilat, inilng);
        var marker = new google.maps.Marker({
            position: userll,
            map: map,
            icon: usericon
        });

        //user geo end
    }

    //markers starts
    var markers = [];

    //markers starts
    // for (var i = 0; i < results.length; i++) {
    //     var object = results[i];
    //     var lat = object.get("lat");
    //     var lng = object.get("lng");
    //     var id = object.get("location_id");

    //     var ll = new google.maps.LatLng(lat, lng);
    //     var marker = new google.maps.Marker({
    //         position: ll,
    //         map: map
    //     });

    //     //one marker evt
    //     google.maps.event.addListener(marker, 'click', function(evt) {
    //         var locatelat = null;
    //         var locatelng = null;
    //         locatelat = this.position.lat();
    //         locatelng = this.position.lng();

    //         //in db starts
    //         db.transaction(function(tx) {
    //             tx.executeSql('INSERT INTO locate(id, lat, lng) VALUES(?,?,?)', [1, locatelat, locatelng], function(tx) {
    //                 //alert("已成功把" + webname + "加入fv");
    //                 f = 1;
    //             });
    //         });
    //         //in db ends
    //     });
    //     //one marker evt
    //     markers.push(marker);
    // }
    //markers end
}
function getNearbyPeople(){
    $.ajax({
        type:'GET',
        url: 'http://140.114.77.15:5000/member/api/v1/search/nearby?distance_km=100000',
        success:function(response){
            result = response;
            alert(result);
            for(var i=0; i<result.length; i++){
                var id = result[i]['id'];
                var portrait = result[i]['portrait'];
                var name = result[i]['name'];
                $('.nearby_people').append('<div class="col-md-4 people_list"><img src="'+portrait+'"/><div>'+name+'</div></div>');
            }
        },
        error:function(error){
            console.log(error);
        }
    });
}