# Web Server SSTT

> Concurrent HTTP/1.1 web server with sockets, keep-alive, cookies and access control.

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![University of Murcia](https://img.shields.io/badge/University%20of%20Murcia-E03B23?style=flat&logo=university&logoColor=white)](https://www.um.es/)

## Overview

**Web Server SSTT** is a concurrent HTTP/1.1 web server that implements persistent connections (Keep-Alive) and state management via cookies. It serves static files with correct MIME types and controls access by limiting the number of requests per client. It includes a basic authentication mechanism via POST form that validates credentials and redirects according to the result, all under a lightweight process model that handles multiple clients simultaneously.

## Demo

<p align="center">
  <video src="https://github.com/user-attachments/assets/2c104638-d827-4300-ba71-d6f69b1fbce7"
    controls width="800"></video>
</p>

## Project structure

```
web-server-sstt/
├── files/                 # Static files served
├── src/                   # Source code
├── .gitignore             # Files and folders ignored by Git
└── README.md              # Main documentation
```

## Requirements

- **Python 3.x**

## Installation

```bash
git clone https://github.com/ibracb/web-server-sstt.git
cd web-server-sstt
```

## Running

### Default values (no arguments):

Starts at `0.0.0.0:8080` serving from `./files`

```bash
python3 src/web_sstt.py
```

### Customising parameters:

Example: local IP, port 3000, custom webroot

```bash
python3 src/web_sstt.py -ip 127.0.0.1 -p 3000 -wb /var/www
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-ip, --host` | Listen IP | `0.0.0.0` |
| `-p, --port` | Server port | `8080` |
| `-wb, --webroot` | Base directory for files | `files` |
| `-v, --verbose` | Debug mode | `False` |

### Help:

```bash
python3 src/web_sstt.py --help
```

## Features

| Functionality | Description |
|---------------|-------------|
| **GET /** | Serves `index.html` and sets cookie `cookie_counter_8959=1` |
| **GET /file** | Serves static file if exists (404 if not) |
| **POST /** | Processes login: email `admin%40profesoresdemurcia8959.org` → `acceso.html`, other → `denegado.html` |
| **Keep-Alive** | Timeout 41s, max 10 requests per connection |
| **Access control** | Counter cookie; at 10 → 403 Forbidden |
| **MIME types** | html, css, js, png, jpg, jpeg, gif, htm |

## Usage examples

**Simple GET request**
```bash
curl -v http://localhost:8080/
```

**Request with cookie (simulates browser)**
```bash
curl -v -b "cookie_counter_8959=1" http://localhost:8080/
```

**POST login**
```bash
curl -v -X POST -d "email=admin%40profesoresdemurcia8959.org" http://localhost:8080/
```

**Failed login**
```bash
curl -v -X POST -d "email=otro%40ejemplo.com" http://localhost:8080/
```

**View Keep-Alive headers**
```bash
curl -v http://localhost:8080/index.html
```

> **Note:** In the browser you write `admin@profesoresdemurcia8959.org` (with `@`). The browser automatically encodes to `%40` when submitting the form. In `curl` you must use the encoded version `admin%40profesoresdemurcia8959.org`.

## Academic context

- **Subject:** Telematic Services
- **Degree:** BSc in Computer Engineering
- **University:** University of Murcia
- **Year:** 2024-2025

## Authors

- **Javier Hernández Soriano** - [jjj3117](https://github.com/jjj3117)
- **Ibrahim Cherif Barry** - [ibracb](https://github.com/ibracb)