    window.tracker = null;


	var loginButton = function(){
	    if (window.tracker == null) {window.tracker = new TrackerAsset();}
		tracker.settings.host = $("#host").val();

		tracker.Login($("#username").val(),$("#password").val(), function(data,error){
			if(!error){
				$( "#login" ).css('background-color','green');
			}else{
				$( "#login" ).css('background-color','red');
			}
		});
	}

	var startButton = function(){
	    if (window.tracker == null) {window.tracker = new TrackerAsset();}
		tracker.settings.host = $("#host").val();
		tracker.settings.trackingCode = $("#trackingCode").val();
		var ut = $("#userToken").val();
		if(ut != "")
			tracker.settings.userToken = ut;

		tracker.Start(function(result, error){
			if(!error){
			    console.log(result);
				$( "#authToken" ).text(result['authToken']);
				$( "#playerId" ).text(result['playerId']);
				$( "#session" ).text(result['session']);
				$( "#actor" ).text(JSON.stringify(result['actor']));
				$( "#start" ).css('background-color','green');

				$(".data").animate({
				left: "+=440",
				});

			}else{
				$( "#start" ).css('background-color','red');
			}
		});
	}

	var trackButton = function(){
		if($("#send_score").is(':checked'))				tracker.setScore($("#score").val());
		if($("#send_completion").is(':checked'))		tracker.setCompletion($("#completion").is(':checked'));
		if($("#send_success").is(':checked'))			tracker.setSuccess($("#success").is(':checked'));
		if($("#send_response").is(':checked'))			tracker.setResponse($("#response").val());

		var t = tracker.Trace($("#verb").val(),$("#target_type").val(),$("#target_id").val())

		$('.trace').animate({
			left: "+=50px",
			bottom: "-=5px",
		});

		$('<div class="box trace"><p>CSV = <span id="csv">' + t.ToCsv() + '</span></p><p>xAPI = <span id="xapi">' + t.ToXapi() + '</span></p></div>').appendTo('.content').animate({
			left: "+=1200px",
		});

		/*$( "#csv" ).text();
		$( "#xapi" ).text();*/
	}

	var flushButton = function(){
		$('.trace').animate({
			left: "+=2000px",
		}, function(){
			$('.trace').remove();
		});

		tracker.Flush(function(result, error){
			if(!error){
				$( "#flush" ).css('background-color','green');
			}else{
				$( "#flush" ).css('background-color','red');
			}
		})
	}

	var addExtensionButton = function(){
		tracker.addExtension($("#key").val(), $("#value").val());
	}

	var addExtensionButtonInt = function(){
		tracker.addExtension($("#keyInt").val(), parseInt($("#valueInt").val()) );
	}
