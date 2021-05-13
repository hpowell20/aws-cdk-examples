// TODO: Requires package.json and tsconfig.json to run the code
const AWS = require('aws-sdk');
const db = new AWS.DynamoDB.DocumentClient();
const uuid_v4 = require('uuid/v4');
const FILE_UPLOAD_BUCKET_NAME = process.env.FILE_UPLOAD_BUCKET_NAME || '';
const FILE_UPLOAD_TABLE_NAME = process.env.FILE_UPLOAD_TABLE_NAME || '';

const RESERVED_RESPONSE = `Error: AWS reserved keywords being used as keywords`;
const DYNAMODB_EXECUTION_ERROR = `Error: DynamoDB error; please take a look at your CloudWatch Logs`;

export const handler = async (event: any = {}) : Promise <any> => {
  const s3Key = event.Records[0].s3.object.key;
  var s3Time = event.Records[0].eventTime;

  const params = {
    TableName: FILE_UPLOAD_TABLE,
    Item: {
        'id': {S: uuid_v4()},
        'file_name': {S: s3Key},
        'timestamp' : {S: s3Time},
    },
  };

//   const params = {
//     TableName: FILE_UPLOAD_TABLE,
//     Item: {
//         'id': uuid_v4(),
//         'file_name': s3Key,
//         'timestamp' : s3Time,
//     },
//   };

  try {
    await db.put(params).promise();

    return {
        statusCode: 201,
        body: ''
    };
  } catch (dbError) {
    const errorResponse = dbError.code === 'ValidationException' && dbError.message.includes('reserved keyword') ?
    DYNAMODB_EXECUTION_ERROR : RESERVED_RESPONSE;

    return {
        statusCode: 500,
        body: errorResponse
    };
  }
};
