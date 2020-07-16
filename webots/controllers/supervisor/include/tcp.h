#ifndef TCP_H
#define TCP_H


int tcp_connect();

int tcp_send(char* data, int data_len);

int tcp_recv(char* buf, int buf_size);

int tcp_close();


#endif // TCP_H
