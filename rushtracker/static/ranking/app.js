(function(){
	var app = angular.module('rankingCreation', []);
	app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);
	app.controller('RankingController', ['$scope', '$http', '$q', 'httpRushService', function( $scope, $http, $q, httpRushService){
		this.ranking = {};
		this.rankList = this.range;
		//this is the list of rankings
		this.rankingList = [];
		var _this = this
		var x = httpRushService.getRushes();
		x.then(function(payload) {
			_this.listOfRushes = payload.data;
			_this.rankList = _this.range();
			_this.ranking.rush = _this.listOfRushes[0];
		});
		var y = httpRushService.getRanks();
		y.success(function(data) {
			_this.rankingList = data;
		});

		this.range = function() {
			var result = [];
			var i;
			for(i = 1; i <= 10; i++) {
				result.push(i);
			}
			return result;
		};

		this.addRanking = function() {

			this.rankingList.unshift(this.ranking);
			this.listOfRushes.splice(this.listOfRushes.indexOf(this.ranking.rush), 1);
			var toSend = {
				'rush': this.ranking.rush.id,
				'rank': this.ranking.rank,
			}
			$http.post('/ranking/submit/', toSend);
			this.ranking = {};
			this.ranking.rush = this.listOfRushes[0];
			
		};

		
	}]);
	app.controller('RankGeneratorController', ['$http', '$q', function($http, $q){
		this.generateReport = function() {
			this.generatedList = [];
			var report = this;
			promise = $http.get('/api/generate-rank-list/');
			promise.success(function(data)
			{
				report.generatedList = data;
			});
		};
	}]);

	app.service('httpRushService', ['$http', function($http) {
		this.getRushes = function() {
			return $http.get('/api/rushRanking/').
			success(function(data, status, headers, config){
			//something funk with scopes and how data is formatted when returned
		});
		}
		this.getRanks = function() {
			return $http.get('/api/ranked/').
			success(function(data, status, headers, config){
			//something funk with scopes and how data is formatted when returned
		});
		}
	}]);
})();