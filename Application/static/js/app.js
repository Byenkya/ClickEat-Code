function sendRequest( method, url, data ){
	
}

function loadProductImage(){
	$('.product-image').each((index, each)=>{
		console.log(each)
		if (each.complete) {
			$(each).attr('hidden', false)
			$(each.dataset.loader).hide()
		}
	})

	$('.product-image').on("load", (event)=>{
		$(event.target).attr('hidden', false)
		$(event.target.dataset.loader).hide()
	})
}

loadProductImage()