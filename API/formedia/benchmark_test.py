import requests
import concurrent.futures
import time

url = "http://127.0.0.1:8000/benchmark/"
file_path = 'clip.mp4'
num_requests = 1  # Total number of requests to be sent
num_concurrent = 2  # Number of concurrent threads

def send_request():
    try:
        files = {'video_file': open(file_path, 'rb')}
        data = {'num_requests': 1}  # Each request will process only 1 request
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error: {e}")
    return {}

def benchmark_test(duration=60, num_threads=num_concurrent):
    start_time = time.time()

    # We want to send a total of num_requests across threads
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Use a list comprehension to submit all tasks
        futures = [executor.submit(send_request) for _ in range(num_requests)]
        
        # Wait for all futures to complete
        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)

        # Collect results after all tasks are completed
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error: {e}")

    # Calculate total number of requests processed and other metrics
    total_requests = len(results)
    if results:
        avg_time_per_request = sum(result.get('total_time', 0) for result in results) / len(results)
        throughput = total_requests / (time.time() - start_time)
        print(f"Total requests processed: {total_requests}")
        print(f"Average time per request: {avg_time_per_request:.2f} seconds")
        print(f"Throughput: {throughput:.2f} requests per second")
    else:
        print("No results received.")

if __name__ == "__main__":
    benchmark_test()
