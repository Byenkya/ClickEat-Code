function printDiv(divName, with_header) {

    var header = document.getElementById(`header-${divName}`);
    if (with_header){
        header.innerHTML = `
                    <div><h1 class="d-inline">Oasis <small>24/7</small></h1></div>
                    Phone: +256-701-085781/0781-599297</br>
                    Rhino Camp Rd, Plot 16 next to WENRECO office</br>
                    Arua Municipal</br>
                    E-mail: oasistwentyfourseven@yahoo.com</br>
                    <hr>`
    }else{
        header.innerHTML = `<div><h1 class="d-inline">Oasis <small>24/7</small></h1></div>`
    }

    var printContents = document.getElementById(divName).innerHTML;
    var originalContents = document.body.innerHTML;
    document.body.innerHTML = printContents;

    window.print();
    document.body.innerHTML = originalContents;

    var header = document.getElementById(`header-${divName}`);
    header.innerHTML = ''

    $(`#${divName}`).modal('hide')
}