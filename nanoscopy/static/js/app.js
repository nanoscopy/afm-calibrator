var ws = null;
var plot = null;

var xmax = options.xmax;

function openWS(){
	ws = new WebSocket("ws://"+window.location.host+"/ws");
	ws.onmessage = _.throttle(function (evt) {
		msg = JSON.parse(evt.data);
		if (options.fft)
		{
			plot.getOptions().yaxes[0].min = -10000;
			plot.getOptions().yaxes[0].max = 60000000000000;
			plot.setData(msg.data);
			plot.setupGrid();
			plot.draw();
		}
		else
		{
			plot.getOptions().yaxes[0].min = -33000;
			plot.getOptions().yaxes[0].max = 33000;
			plot.setData(msg.data);
			plot.setupGrid();
			plot.draw();
		}
		$('#kCalc').val(msg.kc);
	},40);
}
	
function closeWS(){
	ws.close();
}

$('#flot').bind("plotselected", function (event, ranges) {	
	options.xmin = parseInt(ranges.xaxis.from);
	options.xmax = parseInt(ranges.xaxis.to);
	if (ws)
		ws.send(JSON.stringify(options));
});

$('#flot').bind("plotunselected", function (event, ranges) {	
	options.xmin = 0;
	options.xmax = xmax;
	if (ws)
		ws.send(JSON.stringify(options));
});

var plot = $.plot("#flot", [d1], {
			xaxis: {transform:  function(v) {return Math.log(v+0.0001); /*move away from zero*/} , tickDecimals: 3 ,
				inverseTransorm: function(v) {return Math.}
				tickFormatter: function (v, axis) {return "10" + (Math.round( Math.log(v)/Math.LN10)).toString().sup();}
                },
			selection: {
				mode: "x"
			},
			yaxis: {transform:  function(v) {return Math.log(v+0.0001); /*move away from zero*/} , tickDecimals: 20 ,
				tickFormatter: function (v, axis) {return "10" + (Math.round( Math.log(v)/Math.LN10)).toString().sup();}
                }
		}
);

updateDownsampling = _.debounce(function(){
	options.downsampling = parseInt($('#downsampling').val()) || 1;
	if (ws)
		ws.send(JSON.stringify(options));
},250);

$('#downsampling').val(options.downsampling);

$('#downsampling').keyup(updateDownsampling);

$('#fft').change(function(){
	options.fft = $('#fft').is(':checked');
	if(ws)
		ws.send(JSON.stringify(options));
});
