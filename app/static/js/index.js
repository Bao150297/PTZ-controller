/*
* @Author: Bao
* @Date:   2021-12-10 08:33:14
* @Last Modified by:   dorihp
* @Last Modified time: 2022-01-08 08:49:45
*/

$(document).ready(() => {

    // Allow camera go to the preset posititon
    $("#preset-list").on("click", ".btn-go-preset", function(){ // Dynamic append event
        axios.post(`/go_to_preset?name=${$(this).data("name")}`)
    })

    // Add up preset to queue
    $("#preset-list").on("click", ".btn-add-ptour", function(){ // Dynamic append event
        var preset_name = $(this).data("name")
        var preset_opt = `<label class="preset-div form-selectgroup-item w-100">
                                <input type="checkbox" name="form-project-manager[]" value="1" class="form-selectgroup-input" >
                                <div class="form-selectgroup-label d-flex align-items-center p-3">
                                    <div class="form-selectgroup-label-content d-flex align-items-center">
                                        <div class="mr-4">
                                            <div class="font-weight-medium preset-name">${preset_name}</div>
                                        </div>
                                        <button class="btn btn-sm btn-danger btn-rm-preset btn-default mr-2" style="display: none;" data-name="${preset_name}">Remove</button>
                                    </div>
                                </div>
                            </label>`
        $("#preset-tour").append(preset_opt)
    })

    // Assign self-remove action for preset in presettour
    $("#preset-tour").on("click", ".btn-rm-preset", function(){
        $(this).closest("label").remove()
    })

    // Do a preset tour
    $("#do_preset_tour").off().on("click", function(event){
        // List all presets currently stay in preset tour div
        var all_preset = []
        $("#preset-tour .preset-name").each(function(index, ele){
            all_preset.push($(ele).text())
        })
        move_to_preset(all_preset)
        // console.log(all_preset)
    })

    // Recusive go through all preset positions
    function move_to_preset(preset_tour){
        if(!preset_tour.length)
            return
        // Let's go
        var des_preset = preset_tour[0]
        axios.post(`/go_to_preset?name=${des_preset}`)
        setTimeout(function(){
            preset_tour = preset_tour.slice(1)
            move_to_preset(preset_tour)
        }, 6000)
    }

    // add preset select tag
    function load_preset(){
        axios.get("/get_preset")
        .then(function(response){
            for(var i of response.data.preset_list){
                var node = `<label class="preset-div form-selectgroup-item w-100">
                                <input type="checkbox" name="form-project-manager[]" value="1" class="form-selectgroup-input" >
                                <div class="form-selectgroup-label d-flex align-items-center p-3">
                                    <div class="form-selectgroup-label-content d-flex align-items-center">
                                        <div class="mr-4">
                                            <div class="font-weight-medium preset-name">${i}</div>
                                        </div>
                                        <button class="btn btn-sm btn-primary btn-go-preset btn-default mr-2" style="display: none;" data-name="${i}">Go</button>
                                        <button class="btn btn-sm btn-secondary btn-add-ptour btn-default" style="display: none;" data-name="${i}">Add to tour</button>
                                    </div>
                                </div>
                            </label>`
                $("#preset-list").append(node)
            }
        }).catch(function(error){
            alert("Failed to load preset list!")
        })
    }

    load_preset()

    axios.get('/get_loc')
    .then(function(response){
        var coor = response.data
        $("#cur_p").html(`P: ${coor.p.toFixed(8)}`)
        $("#cur_t").html(`T: ${coor.t.toFixed(8)}`)
        $("#cur_z").html(`Z: ${coor.z.toFixed(8)}`)
    })

    var player = videojs('player')
    player.play()

    // Event handle for select tag
    // Iterate over each select element
    $('select').each(function () {
        // Cache the number of options
        var $this = $(this),
            numberOfOptions = $(this).children('option').length

        // Hides the select element
        $this.addClass('s-hidden')

        // Wrap the select element in a div
        $this.wrap('<div class="select"></div>')

        // Insert a styled div to sit over the top of the hidden select element
        $this.after('<div class="styledSelect"></div>')

        // Cache the styled div
        var $styledSelect = $this.next('div.styledSelect')

        // Show the first select option in the styled div
        $styledSelect.text($this.children('option').eq(0).text())

        // Insert an unordered list after the styled div and also cache the list
        var $list = $('<ul />', {
            'class': 'options'
        }).insertAfter($styledSelect)

        // Insert a list item into the unordered list for each select option
        for (var i = 0; i < numberOfOptions; i++) {
            $('<li />', {
                text: $this.children('option').eq(i).text(),
                rel: $this.children('option').eq(i).val()
            }).appendTo($list)
        }

        // Cache the list items
        var $listItems = $list.children('li')

        // Show the unordered list when the styled div is clicked (also hides it if the div is clicked again)
        $styledSelect.click(function (e) {
            e.stopPropagation()
            $('div.styledSelect.active').each(function () {
                $(this).removeClass('active').next('ul.options').hide()
            })
            $(this).toggleClass('active').next('ul.options').toggle()
        })

        // Hides the unordered list when a list item is clicked and updates the styled div to show the selected list item
        // Updates the select element to have the value of the equivalent option
        $listItems.click(function (e) {
            e.stopPropagation()
            $styledSelect.text($(this).text()).removeClass('active')
            $this.val($(this).attr('rel'))
            $list.hide()
            // alert($this.val())
            // Display moving style div according to user's selection
            if($this.attr("name")=="select_move"){
                var selected_move = $this.val()
                $(".move-div").each((index, ele) => {
                    if($(ele).data("move") == selected_move){
                        $(ele).removeClass("d-none")
                        $(ele).addClass("d-block")
                    }
                    else{
                        $(ele).addClass("d-none")
                        $(ele).removeClass("d-block")
                    }
                })
            }
        })

        // Hides the unordered list when clicking outside of it
        $(document).click(function () {
            $styledSelect.removeClass('active')
            $list.hide()
        })
    })

    // Request cotinouse move
    $(".direct").each((index, ele) => {
        $(ele).off().on("click", (e) => {
            var direction = $(ele).data("name")
            axios.post(`/direct?d=${direction}&t=con`)
            .then(function(response){
                if(direction == 'stop')
                    store_cur_ptz()
            })
        })
    })


    // Request absolute move
    $("#do_abs_move").off().on("click", () => {
        var abs_pan  = $("input[name='abs_pan']").val()
        var abs_tilt = $("input[name='abs_tilt']").val()
        var abs_zoom = $("input[name='abs_zoom']").val()
        axios.post(`/direct?t=abs`,
            data={pan: abs_pan, tilt: abs_tilt, zoom: abs_zoom},
            {headers:
                {'Content-Type': 'application/json'}
            })
        .then(function (response) {
            store_cur_ptz()
        })
    })
    // Request relative move
    $("#do_rel_move").off().on("click", () => {
        var rel_pan  = $("input[name='rel_pan']").val()
        var rel_tilt = $("input[name='rel_tilt']").val()
        var rel_zoom = $("input[name='rel_zoom']").val()
        axios.post(`/direct?t=rel`,
            data={pan: rel_pan, tilt: rel_tilt, zoom: rel_zoom},
            {headers:
                {'Content-Type': 'application/json'}
            })
        .then(function(response){
            store_cur_ptz()
        })
    })

    function store_cur_ptz(){
        // Values from current PTZ position will be accquire to previous
        var pre_p = parseFloat($("#cur_p").html().split(":")[1]).toFixed(8)
        var pre_t = parseFloat($("#cur_t").html().split(":")[1]).toFixed(8)
        var pre_z = parseFloat($("#cur_z").html().split(":")[1]).toFixed(8)

        // Change display
        $("#pre_p").html(`P: ${pre_p}`)
        $("#pre_t").html(`T: ${pre_t}`)
        $("#pre_z").html(`Z: ${pre_z}`)

        // Update current PTZ position
        setTimeout(function(){
            axios.get('/get_loc')
            .then(function(response){
                var coor = response.data
                $("#cur_p").html(`P: ${coor.p.toFixed(8)}`)
                $("#cur_t").html(`T: ${coor.t.toFixed(8)}`)
                $("#cur_z").html(`Z: ${coor.z.toFixed(8)}`)
            })
        }, 5000)
    }

    $("#back_prv").off().on("click", function(e){
        e.preventDefault()
        var pre_p = parseFloat($("#pre_p").html().split(":")[1])
        var pre_t = parseFloat($("#pre_t").html().split(":")[1])
        var pre_z = parseFloat($("#pre_z").html().split(":")[1])

        axios.post(`/direct?t=abs`,
            data={pan: pre_p, tilt: pre_t, zoom: pre_z},
            {headers:
                {'Content-Type': 'application/json'}
            })
        .then(function(response){
            store_cur_ptz()
        })
    })

    // Re-useable sweet alert boxes
    function showLoading(title, timer=3600000, callback=null) {
        var toastMixin = Swal.mixin({
            toast: true,
            title: title,
            animation: true,
            position: 'top',
            showConfirmButton: false,
            allowEscapeKey: false,
            timer: timer,
            progressSteps: true,
            onOpen: () => {
                Swal.showLoading()
            },
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        })
        toastMixin.fire({
            animation: true,
        }).then(
           () => {
                if(callback)
                    callback(arguments[3])
           },
           (dismiss) => {}
        )
    }

    // Init canvas for point-click-move function
    var ctx = null
    var canvas = null
    var canvas_w = 0, canvas_h = 0
    function init(){
        var canvas = document.createElement('canvas')
        canvas.setAttribute('style', `width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 4;border: 2px solid #206bc4;`)
        canvas.setAttribute('id', 'point-loc')
        if(typeof G_vmlCanvasManager != 'undefined') {
            canvas = G_vmlCanvasManager.initElement(canvas)
        }
        showLoading("Getting ready...", 600)
        var canvasDiv = document.getElementById("vid-container")
        setTimeout(()=>{
            canvas.setAttribute('height', $(canvasDiv).outerHeight())
            canvas.setAttribute('width', $(canvasDiv).outerWidth())
            canvas_w = canvas.scrollWidth
            canvas_h = canvas.scrollHeight
            ctx = canvas.getContext("2d")
        }, 600)
        canvasDiv.appendChild(canvas)
        canvas.addEventListener("click", point_loc)

        setTimeout(()=>{
            var hr = document.createElement('hr')
            hr.setAttribute('style', `width: 100%; height: 1px; position: absolute; top: ${canvas_h / 2}px; left: 0; z-index: 2;background-color:red;border:none`)
            hr.classList.add('m-0')
            canvasDiv.appendChild(hr)

            var hr2 = document.createElement('hr')
            hr2.setAttribute('style', `width: 1px; height: 100%; position: absolute; top: 0; left: ${canvas_w / 2}px; z-index: 3;background-color:red;border:none`)
            hr2.classList.add('m-0')
            canvasDiv.appendChild(hr2)

        }, 1000)
    }

    init()

    // Get location when click on canvas
    function point_loc(e) {
        var offset = $(this).offset()
        var x = parseInt(e.pageX - offset.left)
        var y = parseInt(e.pageY - offset.top)

        var scale_x = 640 / canvas_w
        var scale_y = 480 / canvas_h

        x *= scale_x
        y *= scale_y

        console.log('scale_x', scale_x, 'scale_y', scale_y, 'x', x, 'y', y)

        axios.post(`/direct?t=rel_c`,
            data = {x: x, y: y},
            {headers:
                {'Content-Type': 'application/json'}
            })
        .then(function(response){
            store_cur_ptz()
        })
    }

    function get_point_loc(canvas, event) {
        var x, y

        canoffset = $(canvas).offset()
        x = event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft - Math.floor(canoffset.left)
        y = event.clientY + document.body.scrollTop + document.documentElement.scrollTop - Math.floor(canoffset.top) + 1

        return [x,y];
    }

    // Save current position as a preset for moving after
    $("#set_preset").off().on('click', function(event) {
        event.preventDefault()
        var preset_name = prompt("Enter this preset's name: ", "A name")
        if(preset_name === null){
            return
        }
        if(!preset_name){
            alert("Cannot leave preset's name empty!")
            return
        }
        axios.post("/save_preset", data={"name": preset_name})
        .then((response) =>{
            alert("Preset saved!")
            // Reload preset list
            $("#preset-list").empty()
            load_preset()
        })
        .catch((error)=>{
            alert(error.message)
        })
    })

    $(document).on('mouseover', '.preset-div', function() {
        $(this).find(".btn-go-preset").show()
        $(this).find(".btn-add-ptour").show()
        $(this).find(".btn-rm-preset").show()
    }).on('mouseout',function(){
        $(this).find(".btn-go-preset").hide()
        $(this).find(".btn-add-ptour").hide()
        $(this).find(".btn-rm-preset").hide()
    })

    // Searching for preset name
    $("#search-preset").on("keyup", function() {
        // Search device by serial number
        var value = $(this).val()

        $(".preset-div").each(function(index, ele) {
            var row_text = $(ele).find(".preset-name").text()
            if (!row_text.includes(value))
                $(ele).hide()
            else
                $(ele).show()
        })
    })

})
