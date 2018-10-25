
    window.tracker = null;

    var show_visualisations = function(){
        xapi();
        completions();
    }

    var completions = function(){
        var items = window.data.completed_items;
        var width = 300,
            height = 150,
            margin = ({top: 20, right: 0, bottom: 30, left: 40}),
            color = d3.scaleOrdinal(d3.schemeCategory10);

        var svg = d3.select("#completed-chart").append("svg")
            .attr("width", width)
            .attr("height", height)

        var x = d3.scaleBand()
            .domain(items.map(d => d.key))
            .range([margin.left, width - margin.right])
            .padding(0.1)

        var y = d3.scaleLinear()
            .domain([0, d3.max(items, d => d.doc_count)]).nice()
            .range([height - margin.bottom, margin.top])

        var xAxis = g => g
            .attr("transform", `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x)
                .tickSizeOuter(0))

        var yAxis = g => g
            .attr("transform", `translate(${margin.left},0)`)
            .call(d3.axisLeft(y))
            .call(g => g.select(".domain").remove())

        var div = d3.select("body").append("div")
    		.attr("class", "tooltip")
    		.style("opacity", 0);

        svg.append("g")
            .attr("fill", "steelblue")
            .selectAll("rect").data(items).enter().append("rect")
            .attr("x", d => x(d.key))
            .attr("y", d => y(d.doc_count))
            .attr("height", d => y(0) - y(d.doc_count))
            .attr("width", x.bandwidth())
            .on("mouseover", function(d) {
                div.transition()
                    .duration(200)
                    .style("opacity", .9);
                div	.html(d.key + ": " + d.doc_count)
                    .style("left", (d3.event.pageX) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
            })
            .on("mouseout", function(d) {
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            });

        svg.append("g")
            .call(xAxis);

        svg.append("g")
            .call(yAxis);


        return svg.node();
    }

	var xapi = function(){
        var touchdowns = window.data.xapi_verbs;
        // d3 donut chart
        var width = 150,
            height = 150,
            radius = Math.min(width, height) / 2,
    		labelr = radius + 30 // radius for label anchor
        var color = d3.scaleOrdinal(d3.schemeCategory10);
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
		    .attr("transform", "translate(" + (radius + 30) + "," + (radius + 50) + ")");
        var div = d3.select("body").append("div")
    		.attr("class", "tooltip")
    		.style("opacity", 0);
        var g = svg.selectAll(".arc")
            .data(pie(touchdowns))
            .enter()
            .append("g")
            .attr("class", "arc")
		    .attr("transform", "translate(" + (radius + 30) + "," + (radius - 75) + ")");
        g.append("path")
            .attr("d", arc)
			.attr("fill", function(d, i) { return color(i); })
        g.on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div	.html(d.data.key + ": "+d.data.doc_count)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
            })
        g.on("mouseout", function(d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        });
        g.append("text")
            .attr("opacity", function(d) { return d.data.doc_count > 1 ? 1 : 0; })
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
            .text(function (d) { return d.data.key + ": "+d.data.doc_count; });
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
