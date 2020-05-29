// initialization
$(document).ready(function () {
    $('select').material_select();
    calcTotalTime();
    checkCurrentBreakpoint();
});

window.onresize = function() { checkCurrentBreakpoint(); };


// globals
var fieldcount = $(".outerIngredientContainer").length;
var lockSendButton = false;


// function to add fields for amounts, ingredients and allergens
function addIngredientField() {
    fieldcount++;
    var amountFieldId = "amount" + fieldcount;
    var labelAmountFieldId = "labelAmount" + fieldcount;
    var ingredientFieldId = "ingredient" + fieldcount;
    var labelIngredientFieldId = "labelIngredient" + fieldcount;
    var allergensCheckFieldId = "allergensCheck" + fieldcount;
    var labelAllergensCheckFieldId = "labelAllergensCheck" + fieldcount;

    $("#ingredientWrapper").append("<div class='outerIngredientContainer'><div class='amountContainer'><div class='input-field'><i class='material-icons prefix'>playlist_add</i><input id='amount' name='amount' type='text' class='validate amounts' data-length='30'><label for='labelAmount'>Amount</label></div></div><div class='ingredientContainer'><div class='input-field'><input id='ingredient' name='ingredient' type='text' class='validate ingredients' data-length='30'><label for='labelIngredient'>Ingredient</label></div><input type='checkbox' class='filled-in allergens' id='allergensCheck' /><label id='labelAllergensCheck' for='allergensCheck'>Allergen?</label></div></div>");
    $('#amount').attr('name', amountFieldId).attr('id', amountFieldId);
    $('#labelAmount').attr('for', amountFieldId).attr('id', labelAmountFieldId);
    $('#ingredient').attr('name', ingredientFieldId).attr('id', ingredientFieldId);
    $('#labelIngredient').attr('for', ingredientFieldId).attr('id', labelIngredientFieldId);
    $('#allergensCheck').attr('name', allergensCheckFieldId).attr('id', allergensCheckFieldId);
    $('#labelAllergensCheck').attr('for', allergensCheckFieldId).attr('id', labelAllergensCheckFieldId);
}

// remove an unused ingredient field
function removeIngredientField() {
    if (fieldcount > 1) {
        $(".outerIngredientContainer").last().remove();
        setTimeout(function () {
            fieldcount--;
        }, 400);
    }
}

//function for onchange event of file input field to convert selected file into base64
//taken from https://www.tutsmake.com/convert-image-to-base64-string-jquery/
function encodeImgtoBase64(element) {
    var file = element.files[0];
    var reader = new FileReader();
    reader.onloadend = function () {
        // writing reader result without mime type information to hidden textarea field to use with form.get() method in python    
        $("#base64file").text(reader.result.split(',')[1]);
    };
    reader.readAsDataURL(file);
}

// calculates the total time for both totalTimeDiv and totalTimeInput field
function calcTotalTime() {
    var totalTimeDiv = parseInt($("#prepTimeDiv").html()) + parseInt($("#cookingTimeDiv").html());
    var totalTimeInput = parseInt($("#prepTime").val()) + parseInt($("#cookingTime").val());

    if (totalTimeDiv || totalTimeInput) {
        if (totalTimeDiv < 60 || totalTimeInput < 60) {
            $("#totalTimeDiv").html(0 + " hrs " + totalTimeDiv + " mins");
            $("#totalTime").html(0 + " hrs " + totalTimeInput + " mins");
        }
        if (totalTimeDiv >= 60 || totalTimeInput >= 60)
            $("#totalTimeDiv").html(parseInt(totalTimeDiv / 60) + " hrs " + totalTimeDiv % 60 + " mins");
        $("#totalTime").html(parseInt(totalTimeInput / 60) + " hrs " + totalTimeInput % 60 + " mins");

    } else {
        $("#totalTimeDiv").html("-");
        $("#totalTime").html("-");
    }
}

// When processing the entered amounts, ingredients and allergens, the field content is read
// and one string for amounts, ingredients and allergens are created. After each value a '#' is added
// as a separator  
function makeIngredientsStrings() {
    var amountsArray = $('.amounts').toArray();
    var ingredientsArray = $('.ingredients').toArray();
    var allergensArray = $('.allergens').toArray();
    var amounts = "",
        ingredients = "",
        allergens = "";
    var i = 0;
    for (i = 0; i < amountsArray.length; i++) {
        amounts = amounts + amountsArray[i].value + "#";
    }
    $('#amountsString').val(amounts);
    i = 0;
    for (i = 0; i < ingredientsArray.length; i++) {
        ingredients = ingredients + ingredientsArray[i].value + "#";
        if (allergensArray[i].checked == true) {
            allergens = allergens + ingredientsArray[i].value + "#";
        }
    }
    $('#ingredientsString').val(ingredients);
    $('#allergensString').val(allergens);
}

// checks if the selected file is of type jpg or jpeg by checking file extension. If that is the case,
// the element in argument list is then encoded into base64 to be uploaded later to image hoster
function validateImageName(element) {
    var enteredFilename = $('#fileinputfield').val();
    if (enteredFilename.endsWith('.jpeg') || enteredFilename.endsWith('.jpg')) {
        encodeImgtoBase64(element);
    } else if (enteredFilename.endsWith('.jpeg') == false || enteredFilename.endsWith('.jpg') == false) {
        $('#resultCheckForValidFields').html("Please select an JPEG or JPG.");
        popupCheckForValidFields();
        $('#fileinputfield').val("");
    }
}

// checks for filled amount and ingredient fields. 
function ingredientfieldsFilled() {
    var amountsArray = $('.amounts').toArray();
    var ingredientsArray = $('.ingredients').toArray();
    var i = 0;
    for (i = 0; i < amountsArray.length; i++) {
        if (amountsArray[i].value == "") {
            return false;
        }
    }
    i = 0;
    for (i = 0; i < ingredientsArray.length; i++) {
        if (ingredientsArray[i].value == "") {
            return false;
        }
    }
    return true;
}

// validation of field length not exceeding maximum 30 chars for ingredient fields and
// 1000 characters for directions field.
function fieldsTooLong() {
    var amountsArray = $('.amounts').toArray();
    var ingredientsArray = $('.ingredients').toArray();
    var i = 0;
    for (i = 0; i < amountsArray.length; i++) {
        if (amountsArray[i].value.length > 30) {
            return true;
        }
    }
    i = 0;
    for (i = 0; i < ingredientsArray.length; i++) {
        if (ingredientsArray[i].value.length > 30) {
            return true;
        }
    }
    if ($('#recipetitle').val().length > 30 || $('#directions').val().length > 1000) {
        return true;
    } else {
        return false;
    }
}

// validation of empty fields on create and edit operation
function fieldvalidation() {
    if ($('#recipetitle').val() == "") {
        $('#resultCheckForValidFields').html("Please give your recipe a title.");
    } else if ($('#dishType').val() == null) {
        $('#resultCheckForValidFields').html("Please give your dish a category.");
    } else if ($('#origin').val() == null) {
        $('#resultCheckForValidFields').html("Please select the origin.");
    } else if ($('#level').val() == null) {
        $('#resultCheckForValidFields').html("Please select the difficulty.");
    } else if ($('#prepTime').val() == "") {
        $('#resultCheckForValidFields').html("Please provide a preparation timeframe.");
    } else if (isNaN($('#prepTime').val())) {
        $('#resultCheckForValidFields').html("Please provide number of minutes for the preparation time.");
    } else if ($('#cookingTime').val() == "") {
        $('#resultCheckForValidFields').html("Please provide a cooking timeframe.");
    } else if (isNaN($('#cookingTime').val())) {
        $('#resultCheckForValidFields').html("Please provide number of minutes for the cooking time.");
    } else if ($('#checkboxUseCurrentFile').length && $('#checkboxUseCurrentFile').is(':checked') == false && $('#fileinputfield').val() == "") {
        $('#resultCheckForValidFields').html("Please provide a picture of your dish.");
    } else if ($('#checkboxUploadFileLater').length && $('#checkboxUploadFileLater').is(':checked') == false && $('#fileinputfield').val() == "") {
        $('#resultCheckForValidFields').html("Please provide a picture of your dish.");
    } else if (ingredientfieldsFilled() == false) {
        $('#resultCheckForValidFields').html("Please fill all ingredient fields or remove fields not needed.");
    } else if ($('#directions').val() == "") {
        $('#resultCheckForValidFields').html("Please fill in the directions.");
    } else if (fieldsTooLong() == true) {
        $('#resultCheckForValidFields').html("Please allow 30 characters per field and 1000 characters for directions text max.");
    } else {
        $('#prepTime').val(parseInt($('#prepTime').val()));
        $('#cookingTime').val(parseInt($('#cookingTime').val()));
        makeIngredientsStrings();
        if (lockSendButton == false) {
            $('#recipeForm').submit();
            lockSendButton = true;
            return;
        }
    }
    if ($('#resultCheckForValidFields').html() != "") {
        popupCheckForValidFields();
    }
    return;
}

// show popup for invalid fields checks
function popupCheckForValidFields() {
    $('#popupCheckForValidFields').css("transform", "translateX(0vw)");
    $('#popupCheckForValidFields').css("opacity", "1.0");
}

// close popup field checks
function closeCheckForValidFieldsPopup() {
    $('#popupCheckForValidFields').css("opacity", "0.0");
    setTimeout(function () {
        $('#resultCheckForValidFields').html("");
        $('#popupCheckForValidFields').css("transform", "translateX(-100vw)");
    }, 400);
}

// close flashes popup
function closeFlashesPopup() {
    $('#flashesPopup').css("opacity", "0.0");
    setTimeout(function () {
        $('#resultCheckForValidFields').html("");
        $('#flashesPopup').css("transform", "translateX(-100vw)");
    }, 400);
}

// show reviews popup in read recipe view
function showReviewsPopup() {
    $('#reviewsPopup').css("transform", "translateX(0vw)");
    $('#reviewsPopup').css("opacity", "1.0");
}

// close reviews popup
function closeReviewsPopup() {
    $('#reviewsPopup').css("opacity", "0.0");
    setTimeout(function () {
        $('#reviewsPopup').css("transform", "translateX(-100vw)");
    }, 400);
}

// show dialog for rating a recipe
function showRatePopup() {
    $('#ratePopup').css("transform", "translateX(0vw)");
    $('#ratePopup').css("opacity", "1.0");
}

// check for filled and max length of form fields in rating dialog and send review to view function.
function sendReview() {
    if ($('#review_title').val() == "") {
        $('#resultCheckForValidFields').html("Please give your review a title.");
        popupCheckForValidFields();
    } else if ($('#level').val() == null) {
        $('#resultCheckForValidFields').html("Please select star level.");
        popupCheckForValidFields();
    } else if ($('#comment').val() == "") {
        $('#resultCheckForValidFields').html("Please provide a short feedback or suggestion");
    } else if ($('#comment').val().length > 30) {
        $('#resultCheckForValidFields').html("Please allow a maximum of 30 characters per comment.");
    }

    if ($('#resultCheckForValidFields').html() != "") {
        popupCheckForValidFields();
    } else {
        $('#ratePopup').css("opacity", "0.0");
        setTimeout(function () {
            $('#ratePopup').css("transform", "translateX(-100vw)");
        }, 400);
        if (lockSendButton == false) {
            $('#rateForm').submit();
            lockSendButton = true;
            return;
        }
    }
}

// cancel review button
function cancelReview() {
    $('#ratePopup').css("opacity", "0.0");
    setTimeout(function () {
        $('#ratePopup').css("transform", "translateX(-100vw)");
    }, 400);
}

// show delete recipe confirmation popup
function showdeleteRecipePopup() {
    $('#deletePopup').css("transform", "translateX(0vw)");
    $('#deletePopup').css("opacity", "1.0");
}

// cancel delete recipe button
function cancelDeleteRecipe() {
    $('#deletePopup').css("opacity", "0.0");
    setTimeout(function () {
        $('#deletePopup').css("transform", "translateX(-100vw)");
    }, 400);
}

// function to check form data in registration form, such as field length, valid email address
// and matching passwords.
function checkRegistrationForm() {
    // mailformat string has been taken from https://www.w3resource.com/javascript/form/email-validation.php
    var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    if ($('#username').val() == "" || $('#email_address').val() == "" || $('#password').val() == "" || $('#password2').val() == "") {
        $('#resultCheckForValidFields').html("Please fill in all fields");
        popupCheckForValidFields();
    } else if ($('#username').val().length > 20) {
        $('#resultCheckForValidFields').html("Please allow username length of 20 character max.");
        popupCheckForValidFields();
    } else if (!$('#email_address').val().match(mailformat)) {
        $('#resultCheckForValidFields').html("Please fill in a valid email address.");
        popupCheckForValidFields();
    } else if ($('#password').val() != $('#password2').val()) {
        $('#resultCheckForValidFields').html("Passwords do not match.");
        popupCheckForValidFields();
    } else {
        if (lockSendButton == false) {
            $('#registrationForm').submit();
            lockSendButton = true;
            return;
        }
    }
}

// function to submit login form
function login() {
    $('#loginForm').submit();
}

// send form on advancedsearch.html
function sendSearchform() {
    $('#searchForm').submit();
}

// function to disable file selection field in case user wants to upload an image later or wants to use
// the current image.
function disableFileInputField() {
    if ($('#checkboxUseCurrentFile').is(':checked') == true || $('#checkboxUploadFileLater').is(':checked') == true) {
        $('#fileinputfield').prop('disabled', true);
    } else {
        $('#fileinputfield').prop('disabled', false);
    }
}

// checks for breakpoint and orientation to call functions to set button width, depending on 
// user's logged on status and being / not being author 
function checkCurrentBreakpoint() {
    // if in landscape mode
    if ($(window).width() > $(window).height()) {
        // landscape mobile
        if ($(window).width() <= 823 && $(window).height() <= 414) {
            setWidthBtnMobile();
        }
        else {
            setWidthBtnDesktop();
        }
    }

    // if in portrait mode
    else if ($(window).width() < $(window).height()) {
        setWidthBtnMobile();
    }
}

// sets button width for desktop
function setWidthBtnDesktop() {
    //check if logged in by checking existence of popup button and set width for 2 buttons to fillup space
    if (!$('#showRatePopupBtn').length) {
        $('#dishType').css("width", "24.7%");
        $('#showReviewsPopupBtn').css("width", "24.7%");
    }
    // if logged in but user is not author
    else if ($('#showRatePopupBtn').length && !$('#editRecipeBtn').length) {
        $('#dishType').css("width", "16.43%");
        $('#showReviewsPopupBtn').css("width", "16.43%");
        $('#showRatePopupBtn').css("width", "16.43%");

    }
    // for author
    else if ($('#editRecipeBtn').length) {
        $('#dishType').css("width", "9.7%");
        $('#showReviewsPopupBtn').css("width", "9.7%");
        $('#showRatePopupBtn').css("width", "9.7%");
        $('#editRecipeBtn').css("width", "9.7%");
        $('#deleteRecipePopupBtn').css("width", "9.7%");
    }
}

// sets button width for mobile
function setWidthBtnMobile() {
    //check if logged in by checking existence of popup button and set width for 2 buttons to fillup space
    var width33 = "32.85%";
    var width50 = "49.65%";
    if (!$('#showRatePopupBtn').length) {
        $('#dishType').css("width", width50);
        $('#showReviewsPopupBtn').css("width", width50);
    }
    // if logged in but user is not author
    else if ($('#showRatePopupBtn').length && !$('#editRecipeBtn').length) {
        $('#dishType').css("width", width33);
        $('#showReviewsPopupBtn').css("width", width33);
        $('#showRatePopupBtn').css("width", width33);
    }
    // for author
    else if ($('#editRecipeBtn').length) {
        $('#dishType').css("width", width33);
        $('#showReviewsPopupBtn').css("width", width33);
        $('#showRatePopupBtn').css("width", width33);
        $('#editRecipeBtn').css("width", width50);
        $('#deleteRecipePopupBtn').css("width", width50);
    }
}
// show side menu on mobile
function showMobileMenu() {
    $('#sideMobileMenu').css("transform", "translateX(4vw)");
}

// hide side menu on mobile
function hideMobileMenu() {
    $('#sideMobileMenu').css("transform", "translateX(-76vw)");
}