var currentURL = window.location;
function initPersonal(){
    $.ajax({
        type:'GET',
        url: 'http://140.114.77.15:'+currentURL.port+'/diary/api/v1/me',
        success:function(response){
            result = response;
            for(var i=0; i<result.length; i++){
                var id = result[i]['Diary']['id'];
                var date = result[i]['Diary']['date'];
                var title = result[i]['Diary']['title'];
                var category = result[i]['Diary']['category'];
                var location = result[i]['Diary']['location'];
                var content = result[i]['Diary']['content'];

                //alert(id+'\n'+date+'\n'+title+'\n'+location);
                
                var split_date = date.split('-');
                var year = split_date[0];
                var month = split_date[1];
                var day = split_date[2];

                switch(month){
                    case "01":
                        month = "January";
                        break;
                    case "02":
                        month = "Febuary";
                        break;
                    case "03":
                        month = "March";
                        break;
                    case "04":
                        month = "April";
                        break;
                    case "05":
                        month = "May";
                        break;
                    case "06":
                        month = "June";
                        break;
                    case "07":
                        month = "July";
                        break;
                    case "08":
                        month = "August";
                        break;
                    case "09":
                        month = "September";
                        break;
                    case "10":
                        month = "October";
                        break;
                    case "11":
                        month = "November";
                        break;
                    case "12":
                        month = "December";
                        break;
                }

                switch(day){
                    case "01":
                        day = day + "st";
                        break;
                    case "02":
                        day = day + "nd";
                        break;
                    case "03":
                        day = day + "rd";
                        break;
                    default:
                        day = day + "th";
                        break;
                }

                $('#diary_grids').append("<div class='col-md-6'><div class='col-xs-5 show_date'>"+year+"<br/>"+month+"<br/>"+day+"</div><div class='col-xs-7'><div class='show_title'>"+title+"</div><div>"+category+"</div><div class='show_location'><img src='../static/images/location.svg'/> "+location+"</div></div><div class='clearfix'> </div><div class='diary_abstract'><p>"+content+"</p></div><div class='more m1 read_btn'><a href='http://140.114.77.15:5000/browse_diary?id="+id+"'>Read More</a></div></div>");
            }
        },
        error:function(error){
            console.log(error);
        }
    });
}
function full_diary(){
    var id = $.url.param('id');
    //alert(id);
    $.ajax({
        type:'GET',
        url: 'http://140.114.77.15:'+currentURL.port+'/diary/api/v1/get?did='+id,
        success:function(response){
            result = response
            
            var date = result[0]['diary']['date'];
            var title = result[0]['diary']['title'];
            var location = result[0]['diary']['location'];
            var content = result[0]['diary']['content'];
            var portrait = result[0]['owner']['portrait'];
            var name = result[0]['owner']['name'];
            //var lat = result[i]['diary']['latitude'];

            if(date==null){
                date='';
            }

            //alert(lat);
            $('#diary_title').append(title);
            $('#diary_date').append(date+' '+location);
            $('#diary_content').append(content);
            $('#author_img').attr("src",portrait);
            $('#author').append(name);
        },   
        error:function(error){
            console.log(error);
        }
    });  

    $.ajax({
        type:'GET',
        url: 'http://140.114.77.15:'+currentURL.port+'/comment/api/v1/get?did='+id,
        success:function(response){
            comment_res = response;
            for(var j=0; j<comment_res.length; j++){
                var comment_content = comment_res[j]['comment']['content'];
                var comment_date = comment_res[j]['comment']['date'];
                var comment_name = comment_res[j]['commentator']['name'];
                var comment_portrait  = comment_res[j]['commentator']['portrait'];

                $('#full_comment').append('<div class="comment_item"><div id="comment_info" class="col-xs-3"><img src="'+comment_portrait+'"/><div>'+comment_name+'</div><div>'+comment_date+'</div></div><div id="comment_content" class="col-xs-9"><p>'+comment_content+'</p></div><div class="clearfix"> </div></div>');
            } 
        },   
        error:function(error){
            console.log(error);
        }
    });
}

function makeComment(){
    var id = $.url.param('id');
    var content = $('textarea[name=user_comment]').val();

    //alert(content);

    $.ajax({
        url: 'http://140.114.77.15:'+currentURL.port+'/comment/api/v1/create',
        data:JSON.stringify({
            content: content,
            did: id
        }),
        type:'POST',
        contentType:"application/json",
        datatype:'application/json',
        success:function(response){
            window.location.reload();
        },
        error:function(error){
            console.log(error);
        }
    });
}