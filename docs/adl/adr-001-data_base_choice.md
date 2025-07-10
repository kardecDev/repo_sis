# ADR

## 001-Database choice

### Context

* Santander has the whitelisting mechanism.

* The only way to connect to the Santander webservices is to do it via VPN.

### Solution

* DevOps engineer from our team has created the VPN that allows us to connect to Santander API.

### Consequences

* You have to have a VPN client installed on your computer. For example [tunnelblick.net](https://tunnelblick.net/downloads.html)

* Each time when you want to run Santander API or integration tests you have to have a VPN connection.

### Status

* APPROVED

### Comment

* Contact XYZ and ask him to provide the VPN config file to you.