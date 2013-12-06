var ws = null;
var plot = null;

var xmax = options.xmax;

function mioLog(valore){
	return Math.log(valore)/Math.LN10;
}

function openWS(){
	ws = new WebSocket("ws://"+window.location.host+"/ws");
	ws.onmessage = _.throttle(function (evt) {
		msg = JSON.parse(evt.data);
		if (options.fft)
		{
			plot.getOptions().xaxes[0].ticks = [0.01,0.1,1,10,100,1000,1e+4];
			plot.getOptions().yaxes[0].ticks = [1,10,100,1000,1e+4,1e+5,1e+6,1e+7,1e+8,1e+9,1e+10,1e+11,1e+12,1e+13,1e+14,1e+14];
			plot.getOptions().yaxes[0].min = 0.001;
			plot.getOptions().yaxes[0].max = 1e+14;
			plot.setData(msg.data);
			plot.setupGrid();
			plot.draw();
		}
		else
		{
			var max = xmax;
			plot.getOptions().xaxes[0].ticks = [0, max/10, 2*max/10, 2*max/10, 3*max/10, 4*max/10, 5*max/10, 6*max/10, 7*max/10, 8*max/10, 9*max/10];
			plot.getOptions().yaxes[0].ticks = [-30000,-20000,-10000,0,10000,20000,30000];
			plot.getOptions().yaxes[0].min = -33000;
			plot.getOptions().yaxes[0].max = 33000;
			plot.setData(msg.data);
			plot.setupGrid();
			plot.draw();
		}
		$('#kCalc').val(msg.kc);
		$('#niR').val(msg.niR);
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
	}
);

$('#flot').bind("plotunselected", function (event, ranges) {	
		options.xmin = 0;
		options.xmax = xmax;
		if (ws)
			ws.send(JSON.stringify(options));
	}
);

var plot = $.plot("#flot", [d1], {
		xaxis: {transform:  function(v) {
					if ($('#fft').is(':checked')) return mioLog(v+0.001);
					else return v;
				} ,
				inverseTransform:  function(v) {
					if ($('#fft').is(':checked')) return Math.pow(10,v);
					else return v;
				} , 
				tickDecimals: 10 ,
				scale: 0.15 ,
				tickFormatter: function (v, axis) {
					if ($('#fft').is(':checked')) return "10" + (Math.round(mioLog(v))).toString().sup();
					else return v;
				}
			},
			selection: {
				mode: "x"
			},
		yaxis: {transform:  function(v) {
					if ($('#fft').is(':checked')) return mioLog(v);
					else return v;
				} ,
				inverseTransform:  function(v) {
					if ($('#fft').is(':checked')) return Math.pow(10,v);
					else return v;
				} ,
				tickDecimals: 10 ,
				tickFormatter: function (v, axis) {
					if ($('#fft').is(':checked')) return "10" + (Math.round( mioLog(v))).toString().sup();
					else return v;
				}
		}
	}
);

updateDownsampling = _.debounce(function(){
		options.downsampling = parseInt($('#downsampling').val()) || 1;
		if (ws)
			ws.send(JSON.stringify(options));
	},
	250);

$('#downsampling').val(options.downsampling);

$('#downsampling').keyup(updateDownsampling);

$('#fft').change(function(){
		options.fft = $('#fft').is(':checked');
		if(ws)
			ws.send(JSON.stringify(options));
	}
);
