(function() {
var app = angular.module('eventManagement', ['ui.bootstrap', 'ui.select', 'ngSanitize']);
	app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

	app.controller('EventController', ['$http', '$state', function($http, $state) {
		var _this = this;
		this.rushList = [];
		var promise = $http.get('/api/events/');


		promise.success(function(data) {
			_this.eventList = data;
		});
	}]);

	app.controller('EventDetailController', ['$http', 'promiseObj', function($http, promiseObj) {
		this.myEvent = promiseObj.data;
	}]);

	app.controller('EventAttendanceController', ['$http', '$stateParams', function($http, $stateParams) {
		var _this = this;
		this.attendance = [];
		$http.get('/api/rush/').then(function(data) {
			_this.rushes = data.data.results;
		});
		$http.get('/api/events/' + $stateParams.id + '/').then(function(data) {
			_this.myEvent = data.data;
			_this.attendance = _this.myEvent.attendance.map(function(obj) {
				return obj.id;
			});
		});
		this.addAttendance = function(rushId) {
			console.log(_this.attendance);
			_this.attendance.push(rushId);
			$http.patch('/api/events/' + $stateParams.id + '/', {'attendance': _this.attendance});
		}
	}]);

})();