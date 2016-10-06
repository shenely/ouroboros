angular.module('ob.core', ['angular-websocket'])
.factory("obRestApi", function ($location, $http, $websocket) {
  var location = $location.host() + ":" + $location.port(),
      restApi =  location + "/ob-rest-api",
      systemApi = $location.protocol()
                + "://" + restApi + "/system",
      processApi = $location.protocol() 
                 + "://" + + restApi + "/process",
      streamApi = ($location.protocol().endsWith("s") ? "wss" : "ws")
                + "://" + restApi + "/stream",
      socket = $websocket(streamApi);
  
  var handlers = {},
      callers = {},
      data = {}, ctrl = {};
  
  socket.onMessage(function (event) {
    var obj = angular.fromJson(event.data);
    if (obj.name in handlers) {
      handlers[obj.name].forEach(function (handler) { handler(obj); });
    }
  });
  
  return {
    "system": {
      "all": function (name) { return $http.get(systemApi); },
      "get": function (name) { return $http.get(systemApi + "?name=" + name); },
      "post": function (config) { return $http.post(systemApi, {"data": config}); },
      "delete": function (name) { return $http.delete(systemApi + "?name=" + name) }
    },
    "process": {
      "all": function (name) { return $http.get(processApi); },
      "get": function (name) { return $http.get(processApi + "?name=" + name); }
    },
    "stream": function (name) {
      handlers[name] = handlers[name] || [];
      callers[name] = callers[name] || { "data": [], "ctrl": [] };
      data[name] = data[name] || [];
      ctrl[name] = ctrl[name] || [];
      
      var handler = function (obj) {              
        if (obj.data !== undefined) {
          obj.data.forEach(function (o) {
            d = data[name].find(function (d) {
              return angular.equals(d.key.$tuple, o.key.$tuple);
            });
            (d !== undefined) ? (d.value = o.value)
                              : data[name].push(o);
          });
          callers[name].data.forEach(function (callback) { callback(); });
        }

        if (obj.ctrl !== undefined) {
          obj.ctrl.forEach(function (o) {
            d = ctrl[name].find(function (d) {
              return angular.equals(d.key, o);
            });
            (d !== undefined) ? (d.value = true)
                              : ctrl[name].push({ "key": o, "value": true });
          });
          callers[name].ctrl.forEach(function (callback) { callback(); });
          ctrl[name].forEach(function (d) { d.value = false; });
        }
      };
      
      return {
        "data": data[name], "ctrl": ctrl[name],
        "pub": {
          "data": function (values) { socket.send(angular.toJson({"data": values})); },
          "ctrl": function (keys) { socket.send(angular.toJson({"ctrl": keys})); }
        },
        "sub": {
          "data": function (callback) { callers[name].data.push(callback); },
          "ctrl": function (callback) { callers[name].ctrl.push(callback); }
        },
        "open": function () { handlers[name].push(handler); },
        "close": function () {
          var index = handlers[name].indexOf(function (d) {
            return d.fn === handler;
          });
          handlers[name].splice(index, 1);
        }
      };
    }
  };
});