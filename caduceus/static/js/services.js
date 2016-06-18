<<<<<<< HEAD
var app = angular.module('caduceus', ['angular-websocket']);

app.factory("caduceus", function ($location, $http, $websocket) {
  var home = $location.host() + ":" + $location.port() + "/caduceus.py";
  
  return function (name, callback) {
    var socket = $websocket("ws://" + home + "/" + name);
    
    var service = {
      "open": function (config) {
        var request = $http.post("http://" + home, config);
        request.then(function (response) {
          var data = [], ctrl = [],
              callers = { "data": [], "ctrl": [] };
          
          socket.onMessage = function onMessage (event) {
            var obj = angular.fromJson(event.data);
        
            try {
              obj.data.forEach(function (o) {
                d = data.find(function (d) { return angular.equals(d.key, o.key); } );
        
                if (d !== undefined) {
                    d.value = o.value;
                } else {
                    data.push(o);
                }
              });
            } catch (error) {
            } finally {
              callers.data
                .filter(function (value) { return value !== null; })
                .forEach(function (callback) { callback(); });
            }
        
            try {
              obj.ctrl.forEach(function (o) {
                var d = ctrl.find(function (d) { return angular.equals(d.key, o); } );
        
                if (d !== undefined) {
                    d.value = true;
                } else {
                    ctrl.push({ "key": o, "value": true });
                }
              });
            } catch (error) {
            } finally {
              callers.ctrl
                .filter(function (value) { return value !== null; })
                .forEach(function (callback) { callback(); });
              
              ctrl.forEach(function (d) { d.value = false; });
            }
          };
          
          var service = {
            "data": {
              "find": function (key) {
                return data.find(function (d) { return angular.equals(d.key, key); } ).value;
              },
              "send": function (values) {
                var message = angular.toJson({ "data": values });
                socket.send(message);
              }
              "watch": function (callback) { return callers.data.push(callback)--; },
              "unwatch": function (i) { callers.data[i] = null; }
            },
            "ctrl": {
              "find": function (key) {
                return ctrl.find(function (d) { return angular.equals(d.key, key); } ).value;
              },
              "send": function (keys) {
                var message = angular.toJson({ "ctrl": keys });
                socket.send(message);
              }
              "listen": function (callback) { return callers.ctrl.push(callback)--; },
              "unlisten": function (i) { callers.ctrl[i] = null; }
            }
          };
          
          callback(service);
        });
        
        return service;
      },
      "close": function () {
        var request = $http.delete("http://" + home + "?" + "name" + "=" + name);
        request.then(function (response) { socket.close(); });
      }
    };
    
    return service;
  };
});
=======
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
>>>>>>> branch 'master' of https://github.com/shenely/ouroboros.git
