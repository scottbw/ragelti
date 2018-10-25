    window.tracker = null;


	var graph = function(){
        var touchdowns = window.data[7].data.buckets[2]['3'].buckets;
        // d3 donut chart
        var width = 300,
            height = 300,
            radius = Math.min(width, height) / 2,
    		labelr = radius + 30 // radius for label anchor
        var color = ['#ff7f0e', '#d62728', '#2ca02c', '#1f77b4'];
        var arc = d3.arc()
            .outerRadius(radius *.6)
            .innerRadius(radius);
        var pie = d3.pie()
            .sort(null)
            .value(function (d) { return d.doc_count; });
        var svg = d3.select("#donut-chart").append("svg")
            .attr("width", width+300)
            .attr("height", height+150)
            .append("g")
		    .attr("transform", "translate(" + (radius + 30) + "," + (radius + 30) + ")");
        var div = d3.select("body").append("div")
    		.attr("class", "tooltip")
    		.style("opacity", 0);
        var g = svg.selectAll(".arc")
            .data(pie(touchdowns))
            .enter()
            .append("g")
            .attr("class", "arc")
		    .attr("transform", "translate(" + (radius + 30) + "," + (radius - 150) + ")");
        g.append("path")
            .attr("d", arc)
            .style("fill", function (d, i) { return color[i]; });
        g.on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div	.html(d.data.key)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            })
        g.on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });
        g.append("text")
            .attr("transform", function(d) {
                var c = arc.centroid(d),
                    x = c[0],
                    y = c[1],
                    // pythagorean theorem for hypotenuse
                    h = Math.sqrt(x*x + y*y);
                return "translate(" + (x/h * labelr) +  ',' +
                    (y/h * labelr) +  ")";
            })
            //.attr("transform", function (d) { return "translate(" + arc.centroid(d) + ")"; })
            .attr("text-anchor", function(d) {
                // are we past the center?
                return (d.endAngle + d.startAngle)/2 > Math.PI ?
                    "end" : "start";
            })
            .attr("dy", ".35em")
            //.style("text-anchor", "middle")
            .style("fill", "black")
            .text(function (d) { return d.data.key; });
    }


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

