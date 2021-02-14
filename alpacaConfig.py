#Get it from alpaca's website. Need to regenerate new ones pretty often whenever you go back onto the web or sum https://api.alpaca.markets
apiKey = 'PKCD15YXHQY9OQE1GLBZ'
secretKey = '4eAE8cNGYEKMofjfNZETeCCOAlMyCKuJf6PvhMM3'
baseUrl = 'https://paper-api.alpaca.markets'#endpoint url. It's paper money rn, but ou can literally change it to 'https://api.alpaca.markets' to trade
# baseUrl = 'https://api.alpaca.markets' #For real trading
dbFile = "D:/AppDbPersonal/app.db"
#Changed dbFile location to D drive because there's more space (Getting historical minute data is a big operation)

EMAIL_ADDRESS = "tradenotifications2@gmail.com"
EMAIL_HOST = "smtp.gmail.com"#Server host -> specifying gmail host
EMAIL_PORT = 465 #Default port
EMAIL_PASSWORD = "Poweryoga1@"



MOTLEY_EMAIL = "tannerfesta@gmail.com"
MOTLEY_PASS = "Poweryoga1@"


"""
context = ssl.create_default_context() #Default context
                    with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
                        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD) #Login
                        email_message = f"Subject: Trade Notifications for {iteratorDate}\n\n" #Our email subject
                        message = f"{symbol} has dec momentum with span_a {data_market['senkou_span_a'][-1]} span_b {data_market['senkou_span_b'][-1]} and close {data_market['close'][-1]}"
                        email_message = "\n\n".join(message) #Our message
                        server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message) #From, to, message (sending to ourself)
                        sys.exit(1)
"""