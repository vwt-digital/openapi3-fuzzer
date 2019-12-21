import json
import adal
import argparse

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('resource', type=str, help='AAD resource, e.g. https://vwt-d-myresource')
  parser.add_argument('tenant', type=str, help='AAD tenant, e.g. beefbeef-beef-beef-beefbeefbeef')
  parser.add_argument('client_id', type=str, help='AAD client id, e.g. beefbeef-beef-beef-beefbeefbeef"')
  parser.add_argument('client_secret', type=str, help='AAD client secret, e.g. MyVeryLongSecrett!!!11"')
  args = parser.parse_args()

params = {
  "resource": args.resource,
  "tenant" : args.tenant,
  "authorityHostUrl" : "https://login.microsoftonline.com",
  "clientId" : args.client_id,
  "clientSecret" : args.client_secret
}

authority_url = (params['authorityHostUrl'] + '/' + params['tenant'])

context = adal.AuthenticationContext(
  authority_url, validate_authority=params['tenant'] != 'adfs',
  )

try:
  token = context.acquire_token_with_client_credentials(
    params['resource'],
    params['clientId'],
    params['clientSecret'])
except Exception as e:
  print(str(e))
  exit(1)

print("{} {}".format(token.get("tokenType"), token.get("accessToken")))
