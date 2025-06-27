import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HttpClientService {
  constructor(private http: HttpClient) {}


  private baseUrl: string = '';

  setBaseUrl(baseUrl: string): void {
    this.baseUrl = baseUrl;
  }

  private buildUrl(url: string): string {
    return this.baseUrl ? `${this.baseUrl}/${url}` : url;
  }

  get<T>(url: string, options?: object): Observable<T> {
    return this.http.get<T>(this.buildUrl(url), options);
  }

  post<T>(url: string, body: any, options?: object): Observable<T> {
    return this.http.post<T>(this.buildUrl(url), body, options);
  }

  put<T>(url: string, body: any, options?: object): Observable<T> {
    return this.http.put<T>(this.buildUrl(url), body, options);
  }

  delete<T>(url: string, options?: object): Observable<T> {
    return this.http.delete<T>(this.buildUrl(url), options);
  }
  setHeaders(headers: HttpHeaders): void {
    // This method is not needed in Angular's HttpClient as headers can be set in each request
    console.warn('setHeaders is not implemented in HttpClientService. Use headers in each request instead.');
  }
  setAuthorizationToken(token: string): void {
    // This method is not needed in Angular's HttpClient as authorization tokens can be set in each request
    console.warn('setAuthorizationToken is not implemented in HttpClientService. Use headers in each request instead.');
  }
  setContentType(contentType: string): void {
    // This method is not needed in Angular's HttpClient as content type can be set in each request
    console.warn('setContentType is not implemented in HttpClientService. Use headers in each request instead.');
  }
  setTimeout(timeout: number): void {
    // This method is not needed in Angular's HttpClient as timeouts can be handled using RxJS operators
    console.warn('setTimeout is not implemented in HttpClientService. Use RxJS operators for timeout handling instead.');
  }
  setResponseType(responseType: 'json' | 'text' | 'blob' | 'arraybuffer' | 'document'): void {
    // This method is not needed in Angular's HttpClient as response type can be set in each request
    console.warn('setResponseType is not implemented in HttpClientService. Use options in each request instead.');
  }
  setWithCredentials(withCredentials: boolean): void {
    // This method is not needed in Angular's HttpClient as withCredentials can be set in each request
    console.warn('setWithCredentials is not implemented in HttpClientService. Use options in each request instead.');
  }
  setParams(params: { [param: string]: string | string[] }): void {
    // This method is not needed in Angular's HttpClient as parameters can be set in each request
    console.warn('setParams is not implemented in HttpClientService. Use options in each request instead.');
  }
  setCache(cache: boolean): void {
    // This method is not needed in Angular's HttpClient as caching is handled by the browser
    console.warn('setCache is not implemented in HttpClientService. Use browser caching instead.');
  }
  setRetry(retry: number): void {
    // This method is not needed in Angular's HttpClient as retries can be handled using RxJS operators
    console.warn('setRetry is not implemented in HttpClientService. Use RxJS operators for retry handling instead.');
  }
}