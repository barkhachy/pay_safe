        <script src="https://hosted.paysafe.com/checkout/v2/paysafe.checkout.min.js"></script>
    
               function checkout() 
               {
                            merchant = {
                                "dynamicDescriptor":"{{data['merchant']['merchantDescriptor']['dynamicDescriptor']}}",
                                "phone":"{{data['merchant']['merchantDescriptor']['phone']}}"
                            }
                            console.log(merchant)
                            //date = "{{dob['day']}}"
                            //console.log(type(date))
                            paysafe.checkout.setup("{{config}}",{
                            "currency": "{{data['currency']}}",
                            "amount": 5000,
                            "locale": "{{data['locale']}}",
                            "customer":
                            {
                                "firstName":"{{customer['firstName']}}",
                                "lastName":"{{customer['lastName']}}",
                                "email":"{{customer['email']}}",
                                "phone":"{{customer['phone']}}",
                                "dateOfBirth":
                                {
                                    "day": 10,
                                    "month":10,////"{{dob['month']}}",
                                    "year":1980//{{dob['year']}}"
                                },
                            },
                            "billingAddress":{
                                "nickName":"{{add['nickName']}}",
                                "street":"{{add['street']}}",
                                "street2":"{{add['street2']}}",
                                "city":"{{add['city']}}",
                                "zip":"{{add['zip']}}",
                                "country":"{{add['country']}}",
                                "state":"{{add['country']}}"
                            },
                            "environment":"{{data['environment']}}",
                            "merchantRefNum":"1559900597607",
                            "canEditAmount":false,
                            "merchantDescriptor":merchant,
                            "displayPaymentMethods":["card"],
                                "paymentMethodDetails": {
                                    "paysafecard": {
                                        "consumerId": "1232323"
                                    },
                                    "paysafecash": {
                                        "consumerId": "123456"
                                    },
                                }
                            }
                            ,function(instance, error, result) {
                                if (result && result.paymentHandleToken) {
                                    console.log(result.paymentHandleToken);
                                    window.open("/payment_sucessful/","_self");
                                    // make AJAX call to Payments API
                                } else {
                                    console.error(error);
                                    alert(error);
                                    //window.open("/payment_unsucessful/","_self");
                                    // Handle the error
                                }
                            }, function(stage, expired) {
                                switch(stage) {
                                    case "PAYMENT_HANDLE_NOT_CREATED": 
                                    // Handle the scenario
                                    window.open("/payment_handle_not_created/","_self");default: // Handle the scenario
                                }
                            });
                        }