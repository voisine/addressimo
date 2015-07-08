FORMAT: 1A

# Addressimo

*Addressimo* is an open source, digital currency address service written in Python. It is available for download here:
 
[**https://github.com/netkicorp/addressimo**](https://github.com/netkicorp/addressimo)

The service provides address retrieving service, which can return the following types based on the request and/or endpoint setup:

* **Static** wallet address
* **BIP0032** wallet address based on an extended master public key
* **BIP0070 PaymentRequest**

An address request to return any of these types of responses can be made to:

**https://site_url/resolve/{id}**

**BIP0032** address generation is based on an extended master public key as well as a Redis-stored blockchain used *address
cache* that is maintained via a cronjob. If an address has been used in a transaction output on the blockchain, the next
index will be tried for the *BIP0032* wallet address generation.

**BIP0070 PaymentRequest** generation can use wallet addresses based on a *static wallet address* or a *BIP0032* generated wallet address that is
generated based on the logic previously explained. *BIP0070 PaymentRequests* are created and signed on demand using the endpoint's configured
private key (or configured signer plugin) and x509 cert.

Additionally, *Addressimo* can act as a **Store & Forward** server for **pre-signed** PaymentRequests. This is particularly useful for purely
mobile wallets that would otherwise need to be online to create and sign *PaymentRequests*. The *Store & Forward* functionality is as follows:

* Register an endpoint
* Add Stored PaymentRequests
* Get Available PaymentRequest Count
* Delete Endpoint

The **Store & Forward PaymentRequests** are available in the same way as the create and sign on demand *PaymentRequests* are retrieved
in the general *Addressimo* address lookup request (described in the top of this document and documented below).

# Group Addressimo

## Address Lookup [GET /resolve/{id}]

**NOTE:** The address lookup can return a simple wallet address via the defined JSON format below **OR** it can return a BIP0070 PaymentRequest.
The response type can be determined by looking at the Content-Type in the API response.

+ Parameters

    - id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Address Resolution ID

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "wallet_address": "1CpLXM15vjULK3ZPGUTDMUcGATGR9xGitv"
        }
        
+ Response 200 (application/bitcoin-paymentrequest)

        Binary PaymentRequest Protobuf
        
+ Response 400 (application/json)

        {
            "success": false,
            "message": "misconfiguration or bad request message"
        }
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "not found message"
        }
        
+ Response 500 (application/json)

        {
            "success": false,
            "message": error_message
        }

## Store & Forward [/sf/{id}]
        
Authentication and verification for this endpoint is based on [BitPay's](https://bitpay.com/api) signed request process.
If you're interested in reading through Bitpay's API documentation regarding the X-Identity and X-Signature headers, please
feel free to check it out [here](https://bitpay.com/api#making-requests).

All requests require both the X-Identity and X-Signature headers to be present and valid. The X-Identity header is the hex-encoded
ECDSA public key for the private key that was used to sign the request. The X-Signature header is the hex-encoded ECDSA signature
of the message that is computed as follows:

privkey.sign( **url** + **request data content** )

For example, when submitting the following request data to https://sf.netki.com/sf:

{"key":"value"}

The API request would have a signature that has signed the string: https://sf.netki.com/sf{"key":"value"}

**NOTE:** The "id" returned in the POST call will need to be used for any further access to the Store & Forward functionality.

### Create Store & Forward Endpoint [POST /sf]
   
+ Request 200 (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "id': "newly_created_endpoint_id",
            "endpoint": "https://site_url/resolve/newly_created_endpoint_id"
        }
        
+ Response 500 (application/json)

        {
            "success": false,
            "message": "error_message"
        }

### Add Presigned PaymentRequests to Store & Forward Endpoint [PUT]

+ Parameters

    + id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Store & Forward Endpoint ID
   
+ Request 200 (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"
            
    + Body

            {
                "presigned_payment_requests": [
                    "HEX ENCODED PRESIGNED & SERIALIZED PaymentRequest #1",
                    "HEX ENCODED PRESIGNED & SERIALIZED PaymentRequest #2",
                    "HEX ENCODED PRESIGNED & SERIALIZED PaymentRequest #N"
                ]
            }

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "payment_requests_added": 5
        }
        
+ Response 400 (application/json)

        {
            "success": false,
            "message": "bad request error message"
        }
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "Invalid Identifier"
        }
        
### Delete Store & Forward Endpoint [DELETE]

+ Parameters

    + id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Store & Forward Endpoint ID
   
+ Request 200 (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"
            
+ Response 204 (application/json)


+ Response 404 (application/json)

        {
            "success": false,
            "message": "Invalid Identifier"
        }
        
### Get Presigned PaymentRequest Count [GET]

+ Parameters

    + id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Store & Forward Endpoint ID
   
+ Request 200 (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "payment_request_count": 5
        }
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "Invalid Identifier"
        }
