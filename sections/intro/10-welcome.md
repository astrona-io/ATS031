# Welcome To The Course

Welcome, and thank you for joining. This course is about one question: how do you set up a Kubernetes cluster so that it is safe from the first day? You will build, break and fix real clusters on your own machine. At the end, you will know what each security setting does and why it matters.

This page tells you who the course is for, what you will be able to do, and how the course works. Read it once before you start. It takes about five minutes.

## Who this course is for

This course is for people who already use Kubernetes and now want to secure it. You should be able to create a pod, a Deployment and a Service with `kubectl`, and read a YAML file without help. You do not need any security background. The course explains every security term the first time it appears.

Many readers prepare for the Certified Kubernetes Security Specialist (CKS) exam. The CKS is a hands-on exam from the Cloud Native Computing Foundation (CNCF) and the Linux Foundation. You solve tasks on live clusters from a terminal, with a time limit. This course covers the Cluster Setup domain of that exam, which is worth 15% of the score. If you do not plan to take the exam, the course still teaches skills you can use at work every day.

## What you will be able to do

The course follows the official Cluster Setup objectives. When you finish, you will be able to:

- Write NetworkPolicy objects that allow only the traffic a pod needs and block the rest.
- Run a CIS benchmark check and fix the findings for the API server, etcd, the kubelet and cluster DNS.
- Set up an Ingress that serves traffic over TLS with a certificate stored in a Secret.
- Block pods from reading node metadata and from reaching node endpoints they do not need.
- Check that a Kubernetes binary is the real file from the release before you run it.

Each of these is a section of the course, and the sections come in this order.

## Words you will see

A few words come back on almost every page. The course uses the real Kubernetes terms, because these are the words you meet in the documentation, in the logs and in the exam.

- **Cluster:** a group of machines that run Kubernetes together.
- **Node:** one machine in the cluster. The control plane node runs the cluster's management parts; a worker node runs your pods.
- **API server (kube-apiserver):** the control plane component that receives every request to the cluster, checks it and stores the result.
- **etcd:** the database where the API server stores the state of the cluster.
- **kubelet:** the agent on each node that starts and stops the containers of a pod.
- **Namespace:** a named group of objects inside a cluster. Many security rules apply to one namespace at a time.
- **Manifest:** a YAML file that describes a Kubernetes object you want to create.

Each module defines the other terms it needs, such as NetworkPolicy, Ingress or Transport Layer Security (TLS), when they first appear.

## The example application

Every example and lab uses the same small application, so you can focus on the security setting and not on a new app each time. The workloads have short names: `bridge`, `scout`, `shuttle`, `probe` and `drifter`. Most of them run in a namespace called `starfleet`, and a second namespace called `outpost` plays the role of another team or an untrusted client.

The names have no technical meaning. They are just easy to tell apart in a command or a log line. In a lab, the namespace names get a number at the end, for example `starfleet-031-010-04-04`, so that each lab has its own namespaces and labs never get in each other's way.

## How the course is laid out

The course has one section for each objective. Each section starts with a short introduction and a list of what you will learn in it. A section then has several modules, and each module covers one topic.

A module has four kinds of pages. The landing page lists the goals, what you should know first and the order of the parts. The parts do the real teaching, one idea per part. A graded lab comes right after the part it practises. The summary page closes the module and repeats the key ideas.

Most modules also come with a playground. A playground is a private, ungraded practice environment that runs on your machine. You use it to follow the hands-on steps in the parts. Labs run in their own separate environment, so you can try things in the playground without any risk to your lab score.

The type of playground depends on what the module teaches. Most modules use kind (Kubernetes in Docker), a tool that runs each Kubernetes node as a container. It starts in about a minute and is enough for work with objects such as NetworkPolicy or Ingress. When a module needs a full machine, for example to work with the files and programs on a node, the playground runs as a QEMU virtual machine instead. QEMU is an emulator that runs a complete operating system on your computer. It takes longer to start and uses more memory, but it behaves like a real server.

## How to read a page

Each part reads like a short chapter of a book. It opens with the problem it solves, explains how the system works, and then shows it on the playground. You run each command yourself and compare your output with the output on the page. Allow about 15 minutes per part, including the hands-on steps.

Each part ends with a "Common pitfalls" box. It lists the mistakes people make most often with that topic. Read it carefully, because many exam tasks test exactly these details.

When you reach a lab, try to solve the task on your own first. The task tells you what the result must look like, and the platform checks your cluster when you submit. Open the solution only when you are done or truly stuck. You learn the most when you find the answer yourself.

Ready? The next page shows you how to set up your machine for the course.
