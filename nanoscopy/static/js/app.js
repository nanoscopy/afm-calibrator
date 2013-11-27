var ws = null;
var plot = null;

var xmax = options.xmax;

function openWS(){
	ws = new WebSocket("ws://"+window.location.host+"/ws");
	
	ws.onmessage = _.throttle(function (evt) {
		plot.setData(JSON.parse(evt.data));
		plot.draw();
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
			selection: {
				mode: "x"
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
