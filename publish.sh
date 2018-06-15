rm seekerAlexaSkill.zip 
zip -r seekerAlexaSkill.zip seekerAlexaSkill
aws lambda update-function-code --function-name seekerAlexaSkill --zip-file fileb://seekerAlexaSkill.zip
