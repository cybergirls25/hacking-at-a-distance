# Hacking at a Distance: Robot-Assisted Attacks on Vulnerable Wireless Systems

A graduation project from Jordan University of Science and Technology (JUST), Faculty of Computer and Information Technology.

Abstract

This project demonstrates how a remotely controlled robot can autonomously perform the MouseJack attack an RF-based exploit targeting wireless mice and keyboards. The robot injects malicious keystrokes into unencrypted 2.4 GHz communication between a dongle and a peripheral.

To defend against this threat, a custom-built Intrusion Detection System (IDS) was developed. The IDS uses both rule-based and machine learning (ML) techniques to detect suspicious USB and HID activity in real time.

---

## Components

## Offensive Tool
- MouseJack attack (via Crazyradio PA)
  - Injects keystrokes into vulnerable dongles
  - Uses Ducky Script and JackIt tools

## Defensive Tool
- Host-based IDS:
  - Detects unusual USB/HID behavior
  - Uses One-Class SVM (ML model) and rule-based logic
  - Logs actions and generates real-time alerts

---

## The Robot

A Raspberry Pi-based mobile robot with:
- RF communication via Crazyradio PA
- Web-based control interface
- Autonomous navigation to get close to the target
- Payload delivery: MouseJack injection scripts

---

## Objectives
- Demonstrate the real-world impact of the MouseJack attack
- Build a scalable IDS to detect injected keystrokes
- Highlight the importance of securing 2.4GHz peripheral communication


---

## Team Members
- Aysha Fahed Oqdeh – afoqdeh21@cit.just.edu.jo
- Shahad Ehab Alnatsheh – sealnatsheh21@cit.just.edu.jo
- Razan Ma'moon Khassawneh – rmkhassawneh21@cit.just.edu.jo 
- Roa’a Moutaz Hamudeh – rmhamudeh21@cit.just.edu.jo

Supervised by Dr. Qasem Abu Al-Haija


---

## Legal Disclaimer

This project was created solely for academic and educational purposes. All tests were conducted in controlled environments on authorized devices. Unauthorized use of these techniques is illegal.
