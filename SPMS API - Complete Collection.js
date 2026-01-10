{
  "info": {
    "name": "SPMS API - Complete Collection (CORRECTED)",
    "description": "Smart Participants Management System (SPMS) - Full API Testing Suite\n\n✅ ALL URLS CORRECTED - Ready to use!\n\nBefore using:\n1. Import this collection into Postman\n2. Run 'Login - Admin' request first\n3. Token will be automatically saved and used for all requests\n\nEngineer Simon Akalees Odiman\nEmail: oakalees@yahoo.com\nPhone: +256 773 965 088 / +256 755 002 896\n\nURL Pattern:\n- Login/Logout: NO /api/v1 prefix (root level)\n- Auth operations: /api/v1/auth/*\n- All modules: /api/v1/{module}/*",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "_exporter_id": "SPMS-v1.0-corrected",
    "version": "1.0.1"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "api_prefix",
      "value": "/api/v1",
      "type": "string"
    },
    {
      "key": "access_token",
      "value": "",
      "type": "string"
    },
    {
      "key": "refresh_token",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "🔐 Authentication",
      "item": [
        {
          "name": "Login - Admin",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "// Save the access token for future requests",
                  "if (pm.response.code === 200) {",
                  "    var jsonData = pm.response.json();",
                  "    pm.collectionVariables.set('access_token', jsonData.access_token);",
                  "    pm.collectionVariables.set('refresh_token', jsonData.refresh_token);",
                  "    console.log('✅ Token saved:', jsonData.access_token.substring(0, 30) + '...');",
                  "    ",
                  "    pm.test('Status code is 200', function() {",
                  "        pm.response.to.have.status(200);",
                  "    });",
                  "    ",
                  "    pm.test('Response has access_token', function() {",
                  "        pm.expect(jsonData).to.have.property('access_token');",
                  "        pm.expect(jsonData.access_token).to.be.a('string');",
                  "    });",
                  "    ",
                  "    pm.test('Response has refresh_token', function() {",
                  "        pm.expect(jsonData).to.have.property('refresh_token');",
                  "    });",
                  "} else {",
                  "    console.log('❌ Login failed');",
                  "    console.log('Status:', pm.response.code);",
                  "    console.log('Response:', pm.response.text());",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/x-www-form-urlencoded"
              }
            ],
            "body": {
              "mode": "urlencoded",
              "urlencoded": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "text"
                },
                {
                  "key": "password",
                  "value": "Ethan@2021",
                  "type": "text",
                  "description": "Default admin password"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/login",
              "host": ["{{base_url}}"],
              "path": ["login"]
            },
            "description": "✅ CORRECTED: Login endpoint (no /api/v1 prefix)\nLogin as admin user. Token is automatically saved for subsequent requests."
          },
          "response": []
        },
        {
          "name": "Login - Staff",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "if (pm.response.code === 200) {",
                  "    var jsonData = pm.response.json();",
                  "    pm.collectionVariables.set('access_token', jsonData.access_token);",
                  "    pm.collectionVariables.set('refresh_token', jsonData.refresh_token);",
                  "    console.log('✅ Staff token saved');",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/x-www-form-urlencoded"
              }
            ],
            "body": {
              "mode": "urlencoded",
              "urlencoded": [
                {
                  "key": "username",
                  "value": "john_staff",
                  "type": "text"
                },
                {
                  "key": "password",
                  "value": "Staff123!",
                  "type": "text"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/login",
              "host": ["{{base_url}}"],
              "path": ["login"]
            },
            "description": "✅ CORRECTED: Login as staff user."
          },
          "response": []
        },
        {
          "name": "Login - Participant",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "if (pm.response.code === 200) {",
                  "    var jsonData = pm.response.json();",
                  "    pm.collectionVariables.set('access_token', jsonData.access_token);",
                  "    pm.collectionVariables.set('refresh_token', jsonData.refresh_token);",
                  "    console.log('✅ Participant token saved');",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/x-www-form-urlencoded"
              }
            ],
            "body": {
              "mode": "urlencoded",
              "urlencoded": [
                {
                  "key": "username",
                  "value": "jane_participant",
                  "type": "text"
                },
                {
                  "key": "password",
                  "value": "Participant123!",
                  "type": "text"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/login",
              "host": ["{{base_url}}"],
              "path": ["login"]
            },
            "description": "✅ CORRECTED: Login as participant user."
          },
          "response": []
        },
        {
          "name": "Get Current User",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 200', function() {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "if (pm.response.code === 200) {",
                  "    var jsonData = pm.response.json();",
                  "    pm.test('Response has user data', function() {",
                  "        pm.expect(jsonData).to.have.property('username');",
                  "        pm.expect(jsonData).to.have.property('role');",
                  "    });",
                  "    console.log('✅ Current user:', jsonData.username, '(Role:', jsonData.role + ')');",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/me",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "me"]
            },
            "description": "✅ CORRECTED: Get current authenticated user information (/api/v1/auth/me)"
          },
          "response": []
        },
        {
          "name": "Refresh Token",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "if (pm.response.code === 200) {",
                  "    var jsonData = pm.response.json();",
                  "    pm.collectionVariables.set('access_token', jsonData.access_token);",
                  "    console.log('✅ Token refreshed');",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"refresh_token\": \"{{refresh_token}}\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/refresh",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "refresh"]
            },
            "description": "✅ CORRECTED: Refresh access token using refresh token"
          },
          "response": []
        },
        {
          "name": "Change Password",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"old_password\": \"Ethan@2021\",\n  \"new_password\": \"NewPassword123!\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/change-password",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "change-password"]
            },
            "description": "✅ CORRECTED: Change current user's password"
          },
          "response": []
        },
        {
          "name": "Logout",
          "request": {
            "method": "POST",
            "header": [],
            "url": {
              "raw": "{{base_url}}/logout",
              "host": ["{{base_url}}"],
              "path": ["logout"]
            },
            "description": "✅ CORRECTED: Logout endpoint (no /api/v1 prefix)\nLogout current user and invalidate token."
          },
          "response": []
        }
      ],
      "description": "Authentication endpoints - Login, logout, and user info\n\n✅ ALL URLS CORRECTED:\n- /login (no /api/v1)\n- /logout (no /api/v1)\n- /api/v1/auth/me\n- /api/v1/auth/*"
    },
    {
      "name": "👥 User Management",
      "item": [
        {
          "name": "Create User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"newuser\",\n  \"password\": \"NewUser123!\",\n  \"full_name\": \"New User\",\n  \"email\": \"newuser@example.com\",\n  \"phone\": \"+256700000000\",\n  \"role\": \"staff\",\n  \"status\": \"active\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/users",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "users"]
            },
            "description": "✅ CORRECTED: Create a new user (/api/v1/auth/users). Admin only."
          },
          "response": []
        },
        {
          "name": "List All Users",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/users",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "users"]
            },
            "description": "✅ CORRECTED: Get all users (/api/v1/auth/users). Admin only."
          },
          "response": []
        },
        {
          "name": "Get User by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/users/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "users", "1"]
            },
            "description": "✅ CORRECTED: Get user details by ID (/api/v1/auth/users/{id}). Admin only."
          },
          "response": []
        },
        {
          "name": "Update User",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"full_name\": \"Updated Name\",\n  \"email\": \"updated@example.com\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/users/2",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "users", "2"]
            },
            "description": "✅ CORRECTED: Update user information. Admin only."
          },
          "response": []
        },
        {
          "name": "Delete User",
          "request": {
            "method": "DELETE",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/users/2",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "users", "2"]
            },
            "description": "✅ CORRECTED: Delete a user (/api/v1/auth/users/{id}). Admin only. Cannot delete own account."
          },
          "response": []
        },
        {
          "name": "Unlock Account",
          "request": {
            "method": "POST",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/admin/unlock-account/john_staff",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "admin", "unlock-account", "john_staff"]
            },
            "description": "✅ CORRECTED: Unlock a locked user account (/api/v1/auth/admin/unlock-account/{username}). Admin only."
          },
          "response": []
        },
        {
          "name": "Change User Role",
          "request": {
            "method": "PATCH",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"new_role\": \"staff\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/auth/admin/change-role/2",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["auth", "admin", "change-role", "2"]
            },
            "description": "✅ CORRECTED: Change user role (/api/v1/auth/admin/change-role/{id}). Admin only. Cannot change own role."
          },
          "response": []
        }
      ],
      "description": "✅ ALL CORRECTED: User management endpoints (/api/v1/auth/users/* and /api/v1/auth/admin/*)"
    },
    {
      "name": "👨‍👩‍👧‍👦 Households",
      "item": [
        {
          "name": "Create Household",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"cluster_name\": \"Rubanga\",\n  \"community\": \"Ethur\",\n  \"village\": \"Aywee\",\n  \"highly_vulnerable\": false,\n  \"food_insecure\": true,\n  \"shelter_insecure\": false\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/households/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["households", ""]
            },
            "description": "Create a new household. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "List All Households",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/households/?skip=0&limit=100",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["households", ""],
              "query": [
                {
                  "key": "skip",
                  "value": "0"
                },
                {
                  "key": "limit",
                  "value": "100"
                },
                {
                  "key": "cluster_name",
                  "value": "Rubanga",
                  "disabled": true
                },
                {
                  "key": "community",
                  "value": "Ethur",
                  "disabled": true
                }
              ]
            },
            "description": "Get all households with optional filters."
          },
          "response": []
        },
        {
          "name": "Get Household by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/households/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["households", "1"]
            },
            "description": "Get a specific household by ID."
          },
          "response": []
        },
        {
          "name": "Get Vulnerable Households",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/households/vulnerable",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["households", "vulnerable"]
            },
            "description": "Get all vulnerable households."
          },
          "response": []
        },
        {
          "name": "Get Household Summary",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/households/1/summary",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["households", "1", "summary"]
            },
            "description": "Get household summary with member statistics."
          },
          "response": []
        },
        {
          "name": "Update Household",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"highly_vulnerable\": true,\n  \"food_insecure\": true\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/households/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["households", "1"]
            },
            "description": "Update household information. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Delete Household",
          "request": {
            "method": "DELETE",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/households/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["households", "1"]
            },
            "description": "Delete a household. Admin only."
          },
          "response": []
        }
      ],
      "description": "✅ CORRECT: Household management endpoints (/api/v1/households/*)"
    },
    {
      "name": "📊 Programmes",
      "item": [
        {
          "name": "Create Programme",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Cash Transfer Program\",\n  \"description\": \"Monthly cash assistance for vulnerable households\",\n  \"start_date\": \"2024-01-01\",\n  \"end_date\": \"2024-12-31\",\n  \"budget\": 50000.00,\n  \"status\": \"active\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/programmes/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["programmes", ""]
            },
            "description": "Create a new programme. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "List All Programmes",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/programmes/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["programmes", ""]
            },
            "description": "Get all programmes."
          },
          "response": []
        },
        {
          "name": "Get Programme by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/programmes/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["programmes", "1"]
            },
            "description": "Get a specific programme by ID."
          },
          "response": []
        },
        {
          "name": "Update Programme",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"status\": \"completed\",\n  \"budget\": 55000.00\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/programmes/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["programmes", "1"]
            },
            "description": "Update programme. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Delete Programme",
          "request": {
            "method": "DELETE",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/programmes/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["programmes", "1"]
            },
            "description": "Delete a programme. Admin only."
          },
          "response": []
        }
      ],
      "description": "✅ CORRECT: Programme management endpoints (/api/v1/programmes/*)"
    },
    {
      "name": "📅 Activities",
      "item": [
        {
          "name": "Create Activity",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"programme_id\": 1,\n  \"name\": \"Skills Training Workshop\",\n  \"description\": \"Vocational skills training for youth\",\n  \"activity_date\": \"2024-02-15\",\n  \"location\": \"Community Hall, Rubanga\",\n  \"max_participants\": 50\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/activities/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["activities", ""]
            },
            "description": "Create a new activity. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "List All Activities",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/activities/?programme_id=1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["activities", ""],
              "query": [
                {
                  "key": "programme_id",
                  "value": "1"
                }
              ]
            },
            "description": "Get all activities, optionally filtered by programme."
          },
          "response": []
        },
        {
          "name": "Get Activity by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/activities/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["activities", "1"]
            },
            "description": "Get a specific activity by ID."
          },
          "response": []
        },
        {
          "name": "Update Activity",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"max_participants\": 60,\n  \"location\": \"New Community Hall\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/activities/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["activities", "1"]
            },
            "description": "Update activity. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Delete Activity",
          "request": {
            "method": "DELETE",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/activities/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["activities", "1"]
            },
            "description": "Delete an activity. Admin only."
          },
          "response": []
        }
      ],
      "description": "✅ CORRECT: Activity management endpoints (/api/v1/activities/*)"
    },
    {
      "name": "✅ Attendance",
      "item": [
        {
          "name": "Record Attendance",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"activity_id\": 1,\n  \"participant_id\": 1,\n  \"status\": \"present\",\n  \"notes\": \"Attended full session\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/attendance/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["attendance", ""]
            },
            "description": "Record attendance for a participant. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Get Activity Attendance",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/attendance/activity/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["attendance", "activity", "1"]
            },
            "description": "Get attendance records for a specific activity."
          },
          "response": []
        },
        {
          "name": "Get Participant Attendance",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/attendance/participant/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["attendance", "participant", "1"]
            },
            "description": "Get attendance history for a specific participant."
          },
          "response": []
        },
        {
         "name": "Generate Attendance Report",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/attendance/report?start_date=2024-01-01&end_date=2024-12-31",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["attendance", "report"],
              "query": [
                {
                  "key": "start_date",
                  "value": "2024-01-01"
                },
                {
                  "key": "end_date",
                  "value": "2024-12-31"
                }
              ]
            },
            "description": "Generate attendance report. Requires staff or admin role."
          },
          "response": []
        }
      ],
      "description": "Attendance tracking endpoints"
    },
    {
      "name": "📋 Surveys",
      "item": [
        {
          "name": "Create Survey",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Baseline Survey\",\n  \"description\": \"Initial assessment of household needs\",\n  \"questions\": [\n    {\n      \"text\": \"How many meals per day?\",\n      \"type\": \"number\"\n    },\n    {\n      \"text\": \"Main source of income?\",\n      \"type\": \"text\"\n    }\n  ],\n  \"status\": \"active\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/surveys/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["surveys", ""]
            },
            "description": "Create a new survey. Admin only."
          },
          "response": []
        },
        {
          "name": "List All Surveys",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/surveys/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["surveys", ""]
            },
            "description": "Get all surveys."
          },
          "response": []
        },
        {
          "name": "Get Survey by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/surveys/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["surveys", "1"]
            },
            "description": "Get a specific survey by ID."
          },
          "response": []
        },
        {
          "name": "Submit Survey Response",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"survey_id\": 1,\n  \"respondent_id\": 1,\n  \"responses\": [\n    {\n      \"question_id\": 1,\n      \"answer\": \"2\"\n    },\n    {\n      \"question_id\": 2,\n      \"answer\": \"Farming\"\n    }\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/surveys/1/responses",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["surveys", "1", "responses"]
            },
            "description": "Submit a survey response. Available to all authenticated users."
          },
          "response": []
        },
        {
          "name": "Get Survey Results",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/surveys/1/results",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["surveys", "1", "results"]
            },
            "description": "Get survey results. Requires staff or admin role."
          },
          "response": []
        }
      ],
      "description": "Survey management endpoints"
    },
    {
      "name": "🔍 Cases",
      "item": [
        {
          "name": "Create Case",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Family Emergency\",\n  \"description\": \"Household needs urgent food assistance\",\n  \"household_id\": 1,\n  \"priority\": \"high\",\n  \"category\": \"emergency\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/cases/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["cases", ""]
            },
            "description": "Create a new case. Available to all authenticated users."
          },
          "response": []
        },
        {
          "name": "List All Cases",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/cases/?status=open",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["cases", ""],
              "query": [
                {
                  "key": "status",
                  "value": "open"
                },
                {
                  "key": "priority",
                  "value": "high",
                  "disabled": true
                }
              ]
            },
            "description": "Get all cases. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Get Case by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/cases/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["cases", "1"]
            },
            "description": "Get a specific case by ID. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Assign Case",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"assignee_id\": 2\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/cases/1/assign",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["cases", "1", "assign"]
            },
            "description": "Assign case to a staff member. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Resolve Case",
          "request": {
            "method": "PATCH",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"resolution\": \"Food assistance provided\",\n  \"status\": \"resolved\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/cases/1/resolve",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["cases", "1", "resolve"]
            },
            "description": "Resolve a case. Requires staff or admin role."
          },
          "response": []
        }
      ],
      "description": "Case management endpoints"
    },
    {
      "name": "📈 Reports",
      "item": [
        {
          "name": "Generate Report",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"report_type\": \"programme_summary\",\n  \"programme_id\": 1,\n  \"start_date\": \"2024-01-01\",\n  \"end_date\": \"2024-12-31\",\n  \"format\": \"pdf\"\n}"
            },
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/reports/generate",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["reports", "generate"]
            },
            "description": "Generate a new report. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "List All Reports",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/reports/",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["reports", ""]
            },
            "description": "Get all generated reports. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Get Report by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/reports/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["reports", "1"]
            },
            "description": "Get a specific report by ID. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Export Report",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/reports/1/export?format=pdf",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["reports", "1", "export"],
              "query": [
                {
                  "key": "format",
                  "value": "pdf",
                  "description": "pdf, excel, or csv"
                }
              ]
            },
            "description": "Export report to file. Requires staff or admin role."
          },
          "response": []
        },
        {
          "name": "Delete Report",
          "request": {
            "method": "DELETE",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/reports/1",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["reports", "1"]
            },
            "description": "Delete a report. Admin only."
          },
          "response": []
        }
      ],
      "description": "Report generation and management endpoints"
    },
    {
      "name": "👥 User Management",
      "item": [
        {
          "name": "Create User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"newuser\",\n  \"password\": \"NewUser123!\",\n  \"full_name\": \"New User\",\n  \"email\": \"newuser@example.com\",\n  \"role\": \"staff\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/users",
              "host": ["{{base_url}}"],
              "path": ["auth", "users"]
            },
            "description": "Create a new user. Admin only."
          },
          "response": []
        },
        {
          "name": "List All Users",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/auth/users",
              "host": ["{{base_url}}"],
              "path": ["auth", "users"]
            },
            "description": "Get all users. Admin only."
          },
          "response": []
        },
        {
          "name": "Get User by ID",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/auth/users/1",
              "host": ["{{base_url}}"],
              "path": ["auth", "users", "1"]
            },
            "description": "Get user details by ID. Admin only."
          },
          "response": []
        },
        {
          "name": "Delete User",
          "request": {
            "method": "DELETE",
            "header": [],
            "url": {
              "raw": "{{base_url}}/auth/users/2",
              "host": ["{{base_url}}"],
              "path": ["auth", "users", "2"]
            },
            "description": "Delete a user. Admin only. Cannot delete own account."
          },
          "response": []
        },
        {
          "name": "Unlock Account",
          "request": {
            "method": "POST",
            "header": [],
            "url": {
              "raw": "{{base_url}}/auth/admin/unlock-account/john_staff",
              "host": ["{{base_url}}"],
              "path": ["auth", "admin", "unlock-account", "john_staff"]
            },
            "description": "Unlock a locked user account. Admin only."
          },
          "response": []
        },
        {
          "name": "Change User Role",
          "request": {
            "method": "PATCH",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"new_role\": \"staff\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/admin/change-role/2",
              "host": ["{{base_url}}"],
              "path": ["auth", "admin", "change-role", "2"]
            },
            "description": "Change user role. Admin only. Cannot change own role."
          },
          "response": []
        }
      ],
      "description": "User management endpoints (Admin only)"
    },
    {
      "name": "💚 Health & System",
      "item": [
        {
          "name": "Health Check",
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/health",
              "host": ["{{base_url}}"],
              "path": ["health"]
            },
            "description": "Check system health. No authentication required."
          },
          "response": []
        },
        {
          "name": "API Info",
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/",
              "host": ["{{base_url}}"],
              "path": [""]
            },
            "description": "Get API information. No authentication required."
          },
          "response": []
        },
        {
          "name": "Detailed API Info",
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}{{api_prefix}}/info",
              "host": ["{{base_url}}{{api_prefix}}"],
              "path": ["info"]
            },
            "description": "Get detailed API information. No authentication required."
          },
          "response": []
        }
      ],
      "description": "System health and information endpoints"
    }
  ]
}