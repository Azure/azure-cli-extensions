{
  "id": "nginx:1.25-alpine",
  "name": "nginx:1.25-alpine",
  "layers": [
    "af70d2752ed4084435638a6bc29243d0dfb963b5dc40ef40dbe61d506881755d",
    "d677bb421ff112833206c65e20cdb95cbeba14740c1aac7df88e7848e3af30a9",
    "fcee4d8911b2794484cb8bf8e2cafacfed443c4ab90096ea5afd434cca1e74e9",
    "1e133baa89894446e550e8120f068ec53441a6839807aaa25b27e16798aa0a4d",
    "1db928b8f92d675449dc15d24ffea0855d5072d64bb1b89aea85f2a4e44f367b",
    "c08e1e04c7dafad80b1571f01b8d7adcce9205702e3bdf68dd0de20129acaf01",
    "c175180cacfc123a931898521e280d53738388e4c95108a28f61339aeca96e32",
    "f07da15381f6470075eb0662d39d693c83c1bc6d5f3dd571b03fe326379fb71f"
  ],
  "mounts": [
    {
      "destination": "/etc/resolv.conf",
      "source": "sandbox:///tmp/atlas/resolvconf/.+",
      "type": "bind",
      "options": [
        "rbind",
        "rshared",
        "rw"
      ]
    }
  ],
  "command": [
    "/docker-entrypoint.sh"
  ],
  "env_rules": [
    {
      "pattern": "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "NGINX_VERSION=1.25.5",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "PKG_RELEASE=1",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "NJS_VERSION=0.8.4",
      "strategy": "string",
      "required": false
    },
    {
      "pattern": "NJS_RELEASE=3",
      "strategy": "string",
      "required": false
    }
  ],
  "signals": [
    3
  ]
}
