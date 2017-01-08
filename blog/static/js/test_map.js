function getusergeo(callback) {
    var inilat = 24.79545;
    var inilng = 120.99834399999997;
    var mapCanvas = document.getElementById("map");
    // var mapCanvas = $( '#map' ); //?????
    var mapOptions = {
        center: new google.maps.LatLng(inilat, inilng),
        zoom: 15
    }
    var map = new google.maps.Map(mapCanvas, mapOptions);
    
}

// function getusergeoagain(firerr) {
//     if (error.code == error.TIMEOUT) {
//         var option = {
//             enableHighAccuracy: false,
//             maximumAge: 600000,
//             timeout: 10000
//         }
//         navigator.geolocation.getCurrentPosition(showPosition, showError, option);
//     }
//     else{
//         showError(firerr);
//     }
// }

function showPosition(latitude,longitude) {
    var inilat = latitude;
    var inilng = longitude;

    //alert(inilat+'\n'+inilng);

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
            //getNearbyPeople();
            //getNearbyDiary();
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

var infowindow_list;
var marker_list;
var diary_list;
function showmap(inilat, inilng) {
    //map starts

    
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

    infowindow_list = new Array();
    marker_list = new Array();
    diary_list = new Array();

    $.ajax({
        type:'GET',
        url: 'http://140.114.77.15:5000/diary/api/v1/search/nearby?distance_km=3',
        success:function(response){
            result = response;
            for(var i=0; i<result.length; i++){
                var id = result[i]['diary']['id'];
                var title = result[i]['diary']['title'];
                var latitude = result[i]['diary']['latitude'];
                var longitude = result[i]['diary']['longitude'];
                
                diary_list.push(Array(id, title, latitude, longitude));
                
            }


            for(var i = 0; i < diary_list.length; i++){

                placeMarker(map,diary_list[i]);
            }
            for(var j = 0; j < marker_list.length; j++){
                marker_list[j].setMap(map);
            }

            var markerCluster = new MarkerClusterer(map, marker_list, {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
            
        },
        error:function(error){
            console.log(error);
        }
    });


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

    //  
    //     });
    //     //one marker evt
    //     markers.push(marker);
    // }
    //markers end
}
function placeMarker(map, diary){
    var marker;
    marker = null;
    var ll = new google.maps.LatLng(diary[2], diary[3]);
    marker = new google.maps.Marker({
        position: ll,
        map: map
    });

    
    var link = 'http://140.114.77.15:5000/browse_diary?id='+diary[0];
    var infoncontent = '<div><div>'+diary[1]+'</div><div class="map_button"><a href='+link+'>Read</a></div></div>';
    var infowindow = new google.maps.InfoWindow({
        content: infoncontent,
        maxWidth: 300
    });
    //one marker evt
    google.maps.event.addListener(marker, 'click', function() {

        // To automaticly close other infowindow when click this marker!
        if(infowindow_list.length !=0){
            for(var j = 0; j < infowindow_list.length; j++){
                infowindow_list[j].close();
            }
        }
        infowindow.open(map, this);
        infowindow_list.push(infowindow);
    });

    marker_list.push(marker);
    marker = null;
}


function getNearbyPeople(){
    $.ajax({
        type:'GET',
        url: 'http://140.114.77.15:5000/member/api/v1/search/nearby?distance_km=3',
        success:function(response){
            result = response;
            
            for(var i=0; i<result.length; i++){
                var id = result[i]['id'];
                var portrait = result[i]['portrait'];
                var name = result[i]['name'];

                //alert(id+'\n'+name);
                $('.nearby_people').append('<a href="http://140.114.77.15:5000/other_profile?id='+id+'"><div class="col-md-4 people_list"><img src="'+portrait+'"/><div>'+name+'</div></div></a>');
            }
        },
        error:function(error){
            console.log(error);
        }
    });
}