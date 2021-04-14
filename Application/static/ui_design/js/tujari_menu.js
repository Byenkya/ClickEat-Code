function runDropDownMenuSettings(){
    // drop down menu toggling
    var menu = $("#toggler").next()
    var parent = $(menu).parent()
    var isSubMenu  = false
    $("#toggler").on("mousedown", function(){
        isSubMenu = false
    })
    $(parent).on("shown.bs.dropdown", function(){
        var dropDownItems = $("#dropdown_category_items").find("a")
        $(dropDownItems).each(function(_, e){
            isSubMenu = true
            $("#all").on("click", function(){
                isSubMenu = false
            })

        })
    })
    $(parent).on("hidden.bs.dropdown", function(){
        if(isSubMenu){
            $(parent).addClass("show")
            $(menu).addClass("show")
            $("#toggler")[0].setAttribute("aria-expanded", "true")
        }
    })
    // end of drop down menu


    // menu for mobile and mobile changes
    runChanges();
    $(window).resize(runChanges)
    function runChanges(){
        $(".home-images").css("height",((42/100)*($(window).width())))
        
        if($(window).width() <= 768){
            $("#tujari-dropdown-menu").css("width",((90/100)*($(window).width())))
            $("a[data-toggle=collapse]").each(function(_,e){
                $(e)[0].setAttribute("aria-expanded", "false")
                
                if($(e).next().hasClass("show")){
                    $(e).next().toggleClass("show");
                }
            })
            $("#items-present-display .product").each(function(_,e){
                $(e).css("width","10rem")
            })
        }
        else if($(window).width() <= 900){
            $("#tujari-dropdown-menu").css("width",((72/100)*($(window).width())))
            $("#advantages_advert_section").css("margin-top",-((33/100)*( $(".home-images").width())))
            $("#cards_advert_section").css("margin-top",((13/100)*($(".home-images").width())))
            $("#items-present-display .product").each(function(_,e){
                $(e).css("width","10rem")
            })
        
            if($("#filters").hasClass("collapse")){
                $("#filters").removeClass("collapse")
            }

        }else{
            $("#advantages_advert_section").css("margin-top",-((29/100)*( $(".home-images").width())))
            $("#cards_advert_section").css("margin-top",((15/100)*($(".home-images").width())))

            $("#tujari-dropdown-menu").css("width",((68/100)*($(window).width())))
            if($("#filters").hasClass("collapse")){
                $("#filters").removeClass("collapse")
            }
        }

    }
}
/////////////////////////////// loading tujari menu //////////////////////////////////
$.ajax({
    url: "/get_menu_categories",
    type: "GET",
    success: function(response,status,xhr){
        if(xhr.status == "200" && status=="success"){
            $(response.categories).each(function(ind,category){
                let tab_active = (ind==0) ? "active" : ""
                let tab_content = (ind == 0) ? "show active" : ""
                let aria_selected = (ind == 0) ? true : false
                $("#dropdown_category_items").append(`
                    <a class="nav-link ${tab_active}" id="${category.name.replace(/ /g,"")}-tab" data-toggle="pill" href="#${category.name.replace(/ /g,"")}" role="tab" aria-controls="${category.name.replace(/ /g,"")}" aria-selected="${aria_selected}">${category.name}</a>
                `)

                $("#tujari-dropdown-menu div.tab-content").append(`
                    <div class="tab-pane fade ${tab_content}" id="${category.name.replace(/ /g,"")}" role="tabpanel" aria-labelledby="${category.name.replace(/ /g,"")}-tab">
                    <div class="d-flex flex-row flex-wrap" id="tab-category-${category.name.replace(/ /g,"")}" >
                    </div>
                    </div>
                `)
                if($(category.sub_category)){
                    $(category.sub_category).each(function(ind,subcategory){
                        $(`div#tab-category-${category.name.replace(/ /g,"")}`).append(`
                            <div class="card border-0 shadow-none flex-fill w-50">
                            <div class="card-body pb-0 pt-3">
                                <h5 class="font-weight-bold mb-0 px-2 text-primary">${subcategory.name}</h5>
                                <div class="d-flex flex-row flex-wrap pl-2" id="div-subcategory-${subcategory.name.replace(/ /g,"")}">

                                </div>
                            </div>
                            </div>
                        `)
                        if(subcategory.product_type){
                            $(subcategory.product_type).each(function(ind,product_type){
                                if(ind == (subcategory.product_type.length - 1)){
                                    $(`div#div-subcategory-${subcategory.name.replace(/ /g,"")}`).append(`
                                        <a class="pt-0 pb-1 pr-0 text-decoration-underline" href="/view_products?product_type=${product_type.name}" >${product_type.name}.</a>
                                    `)
                                }else{
                                    $(`#div-subcategory-${subcategory.name.replace(/ /g,"")}`).append(`
                                        <a class="pt-0 pb-1 pr-0 text-decoration-underline" href="/view_products?product_type=${product_type.name}" >${product_type.name},</a>
                                    `)
                                }
                            })
                        }

                    })
                }
             //////////////////// mobile menu ///////////////////////////////////////////
                $("#accordionMenu").append(`
                    <div class="card rounded-0">
                        <div class="card-header py-2" id="hdr-${category.id}">
                        <a href="#" class="nav-link py-0" role="button" data-toggle="collapse" data-target="#elmt-${category.id}" aria-expanded="false" aria-controls="elmt-${category.id}">${category.name}</a>
                        </div>
                        <div class="overflow-auto" style="max-width:100%">
                        <div id="elmt-${category.id}" class="collapse pb-3 px-4 text-nowrap" aria-labelledby="hdr-${category.id}" data-parent="#accordionMenu">
                        </div>
                        </div>
                    </div>
                `)
                if(category.sub_category){
                    $(category.sub_category).each(function(_,subcategory){
                        $(`div#elmt-${category.id}`).append(`
                            <div class="card border-0 shadow-none">
                            <div class="card-body pb-0 pt-3">
                                <h5 class="font-weight-bold mb-0 text-primary">${subcategory.name}</h5>
                                <div id="elmt-${category.name.replace(/ /g,"")}-${subcategory.name.replace(/ /g,"")}" class="d-flex flex-row flex-wrap"></div>
                            </div>
                            </div>
                        `)
                        if(subcategory.product_type){
                            $(subcategory.product_type).each(function(ind,product_type){
                                if(ind == (subcategory.product_type.length - 1)){
                                    $(`div#elmt-${category.name.replace(/ /g,"")}-${subcategory.name.replace(/ /g,"")}`).append(`
                                        <a class="pt-0 pb-1 pr-0 pl-2 text-decoration-underline black-text" href="/view_products?product_type=${product_type.name}" >${product_type.name}.</a>
                                    `)
                                }else{
                                    $(`div#elmt-${category.name.replace(/ /g,"")}-${subcategory.name.replace(/ /g,"")}`).append(`
                                        <a class="pt-0 pb-1 pr-0 pl-2 text-decoration-underline black-text" href="/view_products?product_type=${product_type.name}" >${product_type.name},</a>
                                    `)
                                }

                            })
                        }
                    })
                }

            })

            runDropDownMenuSettings();
        }
    }
})