var app = angular.module('web', []);

app.controller('WebCtrl', function($scope, $http){
	$scope.sous_rub = [];
	$scope.elements = [];
	$http.post('http://localhost:5000/', "").success(function(data, status) {
		$scope.rubriques = data;
		
		for(i=0; i<$scope.rubriques.length; i++){
			$scope.sous_rub.push($scope.rubriques[i].sous_rub);
		}
		for(i=0; i<$scope.sous_rub.length; i++){
			$scope.elements.push($scope.sous_rub[i].titre);
		}		
	}).error(function(data){
	});
});


