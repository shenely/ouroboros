angular.module('kepler.services', [])
	.factory("cartograph", function() {
		return function(width, height) {			
			var projection = d3.geo.equirectangular()
			    .translate([ width / 2, height / 2])
			    .scale(height / Math.PI);
			
			return d3.geo.path().projection(projection);
		};
	})
	.factory("world", ["$http", function($http) {
		return $http.get("/static/dat/world-110m.json");
	}])
	.factory("ouroboros", function () {
	    var socket = new WebSocket("ws://" + location.host + "/data"),
	        data = Array(),
	        callers = Array();

		socket.onmessage = function(event) {
			obj = JSON.parse(event.data)

			obj.forEach(function (o) {
			    d = data.find(function (d) { return angular.equals(d.key,o.key); } );

			    if (d !== undefined) {
			        d.value = o.value;
			    } else {
			        data.push(o);
			    }
			});

			    callers.forEach(function (caller) { caller(data); });
		};

	    return {
	        data: function (callback) { callers.push(callback) },
	        ctrl: function (callback) {}
	    };
	});