Content-Type: multipart/mixed; boundary="===============1483225219990049239=="
MIME-Version: 1.0
Number-Attachments: 1

--===============1483225219990049239==
MIME-Version: 1.0
Content-Type: text/cloud-config
Content-Disposition: attachment; filename="part-001"

#cloud-config
chpasswd:
  expire: false
  users:
  - name: root
    password: $2b$12$Wck/A00rrXY0Bstahx4pPeS.AtZ5ZIH2l3ks8OEjDHx3atARln3OO
    type: hash
users:
- name: root
  ssh_authorized_keys:
  - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCTVfMPqZRBvj/dhbmkOZFCJ2BehuVstz20Kd4xSs8KJ5sE4I+ylaeAl0PTlF9wziB+N/u3PzBfZvBUZtlh5ZmHGcO/Iw9NOqR3QR3Wjjw3HuLzOJo9Aa0KpqYbHYIuzmyfIx1dHTQ09rHihPdApHJrtOdZI3E4HN1YpbNbFy2ztmphwbms0xCxXrqlXoK1QFOIUbGSvP8blG3v+2YTl2iXvBXwBhKkHkay/Nc1R2SBMuo3V9kE658mQZSzcWtudSDJrMyTF10aO1wI/MUtDInWvH9Xv4RepA6RHNwYIUdjYod2RWYP9RLGfxuu4Hc73TKR/r/LfJU2Ctu7E9lhpqTp
    rsa-key-20250716

--===============1483225219990049239==--
